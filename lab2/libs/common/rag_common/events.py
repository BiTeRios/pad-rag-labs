"""События между сервисами через RabbitMQ.

- Exchange `rag.events` (topic): routing key = тип события, например `documents.changed`.
- У каждого потребителя своя durable-очередь; сообщения persistent, подтверждение (ack) после обработки.
- Ошибка обработчика → повторы с паузой; после max_retries сообщение уходит в `<очередь>.dead`
  (dead-letter exchange `rag.events.dead`), чтобы не блокировать очередь и не потеряться.
- Обработчики идемпотентны: повторная доставка того же события не ломает данные.
- Сервис стартует и при недоступном брокере: подключение повторяется в фоне, /ready показывает его состояние.
"""

import asyncio
import json
import logging
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime

import aio_pika
from aio_pika.abc import AbstractIncomingMessage

from rag_common.errors import ServiceUnavailable
from rag_common.logging import request_id_var

EXCHANGE = "rag.events"
DEAD_LETTER_EXCHANGE = "rag.events.dead"

log = logging.getLogger("rag_common.events")


@dataclass
class Event:
    type: str
    payload: dict
    source: str = ""
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    occurred_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    request_id: str | None = None

    def to_json(self) -> bytes:
        return json.dumps(asdict(self), ensure_ascii=False).encode("utf-8")

    @classmethod
    def from_json(cls, body: bytes) -> "Event":
        return cls(**json.loads(body))


Handler = Callable[[Event], Awaitable[None]]


@dataclass
class _Subscription:
    queue: str
    routing_keys: tuple[str, ...]
    handler: Handler


class RabbitEventBus:
    def __init__(self, url: str, source: str, *, max_retries: int = 3, retry_delay_s: float = 2.0, prefetch: int = 4):
        self.url = url
        self.source = source
        self.max_retries = max_retries
        self.retry_delay_s = retry_delay_s
        self.prefetch = prefetch
        self._subscriptions: list[_Subscription] = []
        self._connection: aio_pika.abc.AbstractRobustConnection | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None
        self._task: asyncio.Task | None = None

    def subscribe(self, queue: str, routing_keys: list[str] | tuple[str, ...], handler: Handler) -> None:
        """Регистрация до start(): очереди объявляются при подключении."""
        self._subscriptions.append(_Subscription(queue, tuple(routing_keys), handler))

    async def start(self) -> None:
        self._task = asyncio.create_task(self._connect_loop(), name="rabbitmq-connect")

    async def _connect_loop(self) -> None:
        delay = 1.0
        while True:
            try:
                self._connection = await aio_pika.connect_robust(self.url)
                break
            except Exception as error:  # noqa: BLE001 — брокер ещё не поднялся: ждём
                log.warning("RabbitMQ недоступен (%s), повтор через %.0f с", type(error).__name__, delay)
                await asyncio.sleep(delay)
                delay = min(delay * 2, 30.0)
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=self.prefetch)
        exchange = await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC, durable=True)
        dead_exchange = await channel.declare_exchange(DEAD_LETTER_EXCHANGE, aio_pika.ExchangeType.DIRECT, durable=True)
        for subscription in self._subscriptions:
            dead_queue = await channel.declare_queue(f"{subscription.queue}.dead", durable=True)
            await dead_queue.bind(dead_exchange, routing_key=subscription.queue)
            queue = await channel.declare_queue(
                subscription.queue, durable=True,
                arguments={"x-dead-letter-exchange": DEAD_LETTER_EXCHANGE, "x-dead-letter-routing-key": subscription.queue},
            )
            for key in subscription.routing_keys:
                await queue.bind(exchange, routing_key=key)
            await queue.consume(self._consumer(subscription))
        self._exchange = exchange
        log.info("RabbitMQ подключён", extra={"queues": [s.queue for s in self._subscriptions]})

    def _consumer(self, subscription: _Subscription):
        async def on_message(message: AbstractIncomingMessage) -> None:
            event = Event.from_json(message.body)
            token = request_id_var.set(event.request_id)
            try:
                for attempt in range(1, self.max_retries + 1):
                    try:
                        await subscription.handler(event)
                    except Exception:  # noqa: BLE001 — любая ошибка обработчика ведёт к повтору
                        log.warning("Ошибка обработки %s (попытка %d/%d)", event.type, attempt, self.max_retries,
                                    exc_info=True, extra={"event": event.type, "event_id": event.event_id})
                        if attempt < self.max_retries:
                            await asyncio.sleep(self.retry_delay_s * 2 ** (attempt - 1))
                        continue
                    await message.ack()
                    log.info("Событие %s обработано", event.type, extra={"event": event.type, "event_id": event.event_id})
                    return
                log.error("Событие %s отправлено в %s.dead", event.type, subscription.queue,
                          extra={"event": event.type, "event_id": event.event_id})
                await message.reject(requeue=False)
            finally:
                request_id_var.reset(token)

        return on_message

    async def publish(self, event_type: str, payload: dict) -> Event:
        if self._exchange is None:
            raise ServiceUnavailable("Брокер сообщений недоступен")
        event = Event(event_type, payload, source=self.source, request_id=request_id_var.get())
        await self._exchange.publish(
            aio_pika.Message(
                event.to_json(), content_type="application/json", delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                message_id=event.event_id, type=event.type,
            ),
            routing_key=event_type,
        )
        log.info("Событие %s опубликовано", event_type, extra={"event": event_type, "event_id": event.event_id})
        return event

    async def check(self) -> None:
        if self._exchange is None or self._connection is None or self._connection.is_closed:
            raise RuntimeError("нет соединения с RabbitMQ")

    async def close(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
        if self._connection is not None:
            await self._connection.close()


class InMemoryEventBus:
    """Для тестов и локального запуска без брокера: события доставляются сразу, в том же процессе."""

    def __init__(self, source: str = ""):
        self.source = source
        self.published: list[Event] = []
        self._subscriptions: list[_Subscription] = []

    def subscribe(self, queue: str, routing_keys, handler: Handler) -> None:
        self._subscriptions.append(_Subscription(queue, tuple(routing_keys), handler))

    async def publish(self, event_type: str, payload: dict) -> Event:
        event = Event(event_type, payload, source=self.source, request_id=request_id_var.get())
        self.published.append(event)
        for subscription in self._subscriptions:
            if event_type in subscription.routing_keys or "#" in subscription.routing_keys:
                await subscription.handler(event)
        return event

    def of_type(self, event_type: str) -> list[Event]:
        return [event for event in self.published if event.type == event_type]

    async def start(self) -> None: ...

    async def check(self) -> None: ...

    async def close(self) -> None: ...


async def publish_safely(bus, event_type: str, payload: dict) -> None:
    """Публикация «уведомительного» события: сбой брокера не должен ломать основной запрос пользователя."""
    try:
        await bus.publish(event_type, payload)
    except Exception:  # noqa: BLE001
        log.warning("Событие %s не опубликовано: брокер недоступен", event_type, exc_info=True, extra={"event": event_type})
