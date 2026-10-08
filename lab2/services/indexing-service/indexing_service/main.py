"""indexing-service: владелец векторного индекса (Qdrant).

Слушает documents.changed (ingestion-service), индексирует изменения, публикует index.updated.
Отдаёт поиск ближайших chunks по вектору для retrieval-service.
Запуск: uvicorn indexing_service.main:create_app --factory --port 8004
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from dataclasses import asdict

from fastapi import FastAPI
from qdrant_client import AsyncQdrantClient

from indexing_service.api import internal, router
from indexing_service.config import Settings
from indexing_service.indexer import Indexer
from indexing_service.store import VectorStore
from rag_common.app import create_app as create_service_app
from rag_common.events import Event, InMemoryEventBus, RabbitEventBus, publish_safely
from rag_common.http import ServiceClient

log = logging.getLogger(__name__)

EVENT_INDEX_UPDATED = "index.updated"
STARTUP_RETRY_S = 15


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    qdrant = app.state.qdrant or (
        AsyncQdrantClient(path=settings.qdrant_path) if settings.qdrant_path
        else AsyncQdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key)
    )
    ingestion = ServiceClient("ingestion-service", settings.ingestion_url, settings.ingestion_timeout_s,
                              transport=app.state.transports.get("ingestion"))
    inference = ServiceClient("inference-service", settings.inference_url, settings.inference_timeout_s,
                              transport=app.state.transports.get("inference"))
    indexer = Indexer(VectorStore(qdrant), ingestion, inference, settings)
    bus = app.state.event_bus
    app.state.indexer = indexer
    app.state.jobs = set()

    async def publish_result(trigger: str, stats, extra: dict | None = None) -> None:
        await publish_safely(bus, EVENT_INDEX_UPDATED, {
            "trigger": trigger, "collection": indexer.store.collection, **asdict(stats),
            "duration_s": (indexer.last_job or {}).get("duration_s"), **(extra or {}),
        })

    async def on_documents_changed(event: Event) -> None:
        payload = event.payload
        stats = await indexer.run_job("event", lambda: indexer.apply(payload["changed"], payload["deleted"]))
        await publish_result("event", stats, {"run_id": payload.get("run_id")})

    async def run_reconcile(trigger: str) -> None:
        try:
            stats = await indexer.run_job(trigger, indexer.reconcile)
        except Exception:  # noqa: BLE001 — итог в last_job, сервис работает дальше
            log.exception("Сверка индекса (%s) не удалась", trigger)
            return
        await publish_result(trigger, stats)

    async def reconcile_on_startup() -> None:
        while True:  # соседи (ingestion, inference) могут подняться позже
            try:
                await indexer.prepare()
                break
            except Exception as error:  # noqa: BLE001
                log.warning("Индекс ещё не готов (%s), повтор через %d с", error, STARTUP_RETRY_S)
                await asyncio.sleep(STARTUP_RETRY_S)
        await run_reconcile("startup")

    app.state.run_reconcile = run_reconcile
    bus.subscribe(settings.events_queue, ["documents.changed"], on_documents_changed)
    await bus.start()
    app.state.ready_checks = {"qdrant": indexer.store.ping, "index": indexer.prepare}
    if isinstance(bus, RabbitEventBus):
        app.state.ready_checks["broker"] = bus.check
    if settings.reconcile_on_startup:
        app.state.jobs.add(asyncio.create_task(reconcile_on_startup()))
    yield
    for task in app.state.jobs:
        task.cancel()
    await bus.close()
    await ingestion.close()
    await inference.close()
    await qdrant.close()


def create_app(settings: Settings | None = None, event_bus=None, qdrant=None, transports: dict | None = None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="indexing-service",
        description="Владелец векторного индекса Qdrant: очистка, chunking и векторизация документов "
                    "по событию documents.changed; поиск ближайших chunks для retrieval-service.",
        routers=[router, internal],
        lifespan=lifespan,
    )
    app.state.event_bus = event_bus or (
        # prefetch=1: пачки обрабатываются по одной, следующая доставляется после ack предыдущей
        RabbitEventBus(settings.rabbitmq_url, settings.service_name, prefetch=1) if settings.rabbitmq_url
        else InMemoryEventBus(settings.service_name)
    )
    app.state.qdrant = qdrant
    app.state.transports = transports or {}  # подмена HTTP-соседей в тестах
    return app
