# Контракт событий (RabbitMQ)

Exchange `rag.events`, тип topic, durable. Routing key — тип события. Сообщения persistent, `content_type: application/json`.

Конверт одинаковый для всех событий (`rag_common/events.py`):

```json
{
  "type": "documents.changed",
  "payload": { },
  "source": "ingestion-service",
  "event_id": "4f0c…",            
  "occurred_at": "2026-10-08T05:31:07.589+00:00",
  "request_id": "8e96db2d…"       
}
```
- `event_id` — уникален; потребители по нему отбрасывают повторы (доставка at-least-once);
- `request_id` — запрос, который вызвал событие: по нему в логах связываются издатель и потребитель.

## documents.changed
Издатель — ingestion-service, после синхронизации, если что-то изменилось. Потребитель — indexing-service (очередь `indexing.documents-changed`).

| Поле | Тип | Смысл |
|------|-----|-------|
| `run_id` | str | запуск синхронизации |
| `commit_sha` | str | коммит источника |
| `changed` | list[str] | добавленные и изменённые документы (id = путь в docs_root) |
| `deleted` | list[str] | удалённые из источника (только в первой пачке) |
| `batch`, `batches` | int | номер пачки и их число: изменения публикуются по `EVENT_BATCH_SIZE` (50) документов |

Пачки нужны из-за времени обработки. Полная переиндексация на CPU одним сообщением шла бы ≈20 минут — это близко к `consumer_timeout` RabbitMQ (30 мин), после которого сообщение доставляется заново. Пачка из 50 документов обрабатывается за 2–3 минуты. indexing-service берёт по одному сообщению (`prefetch=1`).

Содержимое документов в событие не кладётся: потребитель забирает его по REST (`POST /internal/documents/batch`). Так сообщения маленькие, а документ, удалённый после события, просто не вернётся.

## index.updated
Издатель — indexing-service, после каждой задачи индексации (событие, сверка при старте, ручная сверка). Потребитель — analytics-service (`analytics.events`).

| Поле | Тип | Смысл |
|------|-----|-------|
| `trigger` | str | `event` \| `startup` \| `manual` |
| `run_id` | str \| null | запуск ingestion, если задача по событию |
| `collection` | str | коллекция Qdrant |
| `added`, `updated`, `unchanged`, `deleted`, `empty` | int | документы |
| `chunks_indexed` | int | векторизовано chunks |
| `duration_s` | float | длительность |

## question.answered
Издатель — chat-service, после каждого ответа, включая отказы. Потребитель — analytics-service.

| Поле | Тип | Смысл |
|------|-----|-------|
| `message_id`, `conversation_id`, `user_id` | str | ответ, диалог, автор |
| `question` | str | текст вопроса (аналитике нужен для «вопросов без ответа») |
| `refused` | bool | «информации недостаточно» |
| `llm_called` | bool | false — контекст не найден, LLM не вызывалась |
| `sources` | list[str] | id документов-источников |
| `model`, `prompt` | str | LLM и промпт |
| `timings_ms` | {retrieval, generation, total} | задержки |
| `degraded` | list[str] | шаги поиска, пропущенные из-за сбоя (например, `reranker`) |
| `context_chunks` | int | сколько chunks получила LLM |

## user.registered
Издатель — auth-service. Потребитель — analytics-service.

| Поле | Тип | Смысл |
|------|-----|-------|
| `user_id` | str | новый пользователь |
| `role` | str | `user` (первый admin создаётся при старте сервиса и события не публикует) |

Email в событие не попадает: аналитике он не нужен.

## Ошибки обработки
Потребитель повторяет обработку 3 раза с паузой 2 → 4 с. Потом сообщение уходит в `<очередь>.dead` через dead-letter exchange `rag.events.dead`. Разобрать его можно в консоли RabbitMQ (`:15672`).
