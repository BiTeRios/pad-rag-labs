# Lab2. RAG по документации Kubernetes как микросервисное приложение

## 1. Описание проекта

RAG-система из Lab1 (вопросы на русском по англоязычной документации Kubernetes) разделена на **7 бизнес-сервисов**, **API Gateway** и инфраструктуру:
- PostgreSQL — отдельная БД у каждого сервиса с состоянием;
- Qdrant — векторный индекс;
- RabbitMQ — события между сервисами.

LLM — локальная Ollama на хосте; для системы это внешний сервис.

Что умеет система:
- регистрация и вход по JWT, роли `user` / `admin`;
- автоматический сбор документации из GitHub: инкрементально, без дублей, с проверкой целостности;
- индексация по событию: изменился документ → пересчитываются только его chunks;
- семантический поиск и ответы на вопросы со ссылками на источники, отказ «информации недостаточно»;
- история диалогов, оценки ответов, аналитика качества: доля отказов, задержки, цитируемые документы;
- веб-интерфейс: чат со ссылками на источники, история, оценки, панель администратора.

Логика конвейера и параметры (chunking, модели, пороги, промпт) — результаты экспериментов Lab1 (`../lab1/README.md`, раздел 10).

## 2. Архитектура

```text
          браузер → web (:8080, nginx: статика + прокси /api) · curl · Swagger UI
                                  │  HTTP :8000
                        ┌─────────▼─────────┐
                        │    API Gateway    │  маршруты · JWT · роли · rate limit · X-Request-ID · /api/status
                        └──┬──┬──┬──┬──┬──┬─┘
          ┌────────────────┘  │  │  │  │  └──────────────────────┐
          ▼                   ▼  │  ▼  ▼                         ▼
   ┌─────────────┐  ┌───────────┐│┌──────────┐ ┌────────────┐ ┌──────────────┐
   │auth-service │  │ ingestion ││ │ indexing │ │ retrieval  │ │ chat-service │
   │ JWT, роли   │  │  -service ││ │ -service │ │ -service   │ │ RAG-ответ,   │
   └──────┬──────┘  └─────┬─────┘│ └──┬───┬───┘ └──┬───┬─────┘ │ история      │
          │PG:auth        │PG:ingestion  │Qdrant    │   │       └──┬────┬──────┘
          │               │      │   ▲   │   ▲      │   │          │PG:chat
          │               │      │   │   │   └──────┘   │ REST     │    │ REST
          │               │      │   │   │ /internal/search          │    ▼
          │               │      │   │   ▼               ▼          │ Ollama (хост, GPU)
          │               │      │  ┌───────────────────────┐       │
          │               │      │  │  inference-service    │◄──────┘ (через retrieval)
          │               │      │  │ e5-base + reranker    │
          │               │      │  └───────────────────────┘
          │               │      └──────────────────► analytics-service ── PG:analytics
          ▼               ▼                              ▲
    ══════════════════ RabbitMQ: exchange rag.events (topic) ═══════════════════
     user.registered   documents.changed → indexing     index.updated, question.answered → analytics
```

### Сервисы

| Сервис | Ответственность | API (через gateway) | Данные |
|--------|-----------------|---------------------|--------|
| **auth-service** | пользователи, bcrypt-пароли, роли, выпуск JWT | `/api/auth/*` | PostgreSQL `auth` |
| **ingestion-service** | синхронизация корпуса с GitHub (grabber из Lab1): SHA, дубли, целостность, история запусков | `/api/ingestion/*` | PostgreSQL `ingestion` |
| **indexing-service** | владелец векторного индекса: очистка, chunking, векторизация по событию, сверка с корпусом, поиск по вектору | `/api/indexing/*`, `/internal/search` | Qdrant |
| **inference-service** | модели: эмбеддинги `multilingual-e5-base` и reranker `bge-reranker-v2-m3`, одна копия весов на систему | только `/internal/*` | веса в томе |
| **retrieval-service** | конвейер поиска из Lab1: вектор → кандидаты → порог → дубли → длина → reranker → top-K | `/api/search` | — (без состояния) |
| **chat-service** | вопрос → поиск → LLM → ответ со ссылками или отказ; диалоги | `/api/chat/*` | PostgreSQL `chat` |
| **analytics-service** | проекция событий: доля отказов, задержки, источники; оценки ответов | `/api/feedback`, `/api/analytics/*` | PostgreSQL `analytics` |
| gateway (не бизнес-сервис) | единая точка входа | все `/api/*`, `/docs/{service}` | — |
| web (не бизнес-сервис) | веб-интерфейс: nginx отдаёт статику, `/api/*` проксирует на gateway | — | — |

### Почему разделено именно так
- **По жизненному циклу данных.** Корпус документов (ingestion), векторный индекс (indexing) и диалоги пользователей (chat) меняются по разным причинам и с разной частотой. У каждого вида данных один владелец.
- **По ресурсам.** Модели занимают ≈3.4 ГБ и требуют CPU/GPU. Они вынесены в inference-service, чтобы держать одну копию весов на систему и масштабировать её отдельно от лёгких сервисов. Индексация и поиск используют одну модель, поэтому векторы гарантированно совместимы.
- **По скорости изменений.** Логика ранжирования (пороги, reranker, top-K — то, что подбиралось в Lab1) живёт в retrieval-service. Её можно менять, не трогая индекс и генерацию.
- **Аналитика — асинхронная проекция.** Она не участвует в ответе пользователю: её недоступность не влияет на чат, а данные догоняются из очереди.

### Взаимодействие
**Синхронно (REST, JSON):**
- gateway → сервисы;
- chat → retrieval → inference (`/internal/embed`, `/internal/rerank`) и indexing (`/internal/search`);
- indexing → ingestion (`/internal/documents/batch`) и inference (`/internal/embed`).

Пути `/internal/*` gateway не проксирует.

**Асинхронно (RabbitMQ, topic exchange `rag.events`):**

| Событие | Издатель | Потребитель | Зачем |
|---------|----------|-------------|-------|
| `documents.changed` | ingestion | indexing | после синхронизации переиндексировать только изменённые и удалить пропавшие документы |
| `index.updated` | indexing | analytics | история обновлений индекса |
| `question.answered` | chat | analytics | доля отказов, задержки, источники; к ответу можно оставить оценку |
| `user.registered` | auth | analytics | число пользователей |

Поля событий — `docs/events.md`.

Гарантии:
- очереди durable, сообщения persistent, подтверждение (ack) — после обработки;
- ошибка обработчика → 3 повтора с паузой → очередь `<имя>.dead`. Сообщение не теряется и не блокирует очередь;
- обработчики идемпотентны: повторная доставка не портит данные. Индексация сравнивает отпечаток документа, аналитика — `event_id`;
- если событие всё же потеряно (брокер был недоступен при публикации), indexing-service сверяет индекс с корпусом при старте и по `POST /api/indexing/reconcile`.

### Сценарий «вопрос → ответ»
```text
POST /api/chat/ask ─► gateway: JWT → X-User-Id/Role, X-Request-ID, rate limit 10/мин
  ─► chat-service ─► retrieval-service /api/search
        ─► inference /internal/embed (вектор вопроса)
        ─► indexing /internal/search (20 кандидатов из Qdrant)
        ─► порог cos 0.78 → дубли → длина → inference /internal/rerank → порог 0.1 → top-5
  ◄─ chunks пусто? → отказ без LLM : Ollama (strict-промпт) → ответ со ссылками [n] → источники
  ─► PostgreSQL chat (история) ─► событие question.answered ─► analytics-service
```
X-Request-ID проходит по всей цепочке: в HTTP-заголовках и в событиях. По нему в логах всех сервисов видна обработка одного запроса.

### Database per service
У каждого сервиса с состоянием — своя БД и свой пользователь PostgreSQL. Права на чужие БД отозваны (`infrastructure/postgres/init-databases.sh`), сервис физически не может прочитать чужие таблицы.

Физически это **один сервер PostgreSQL**. Причина — экономия ресурсов в Compose и Minikube. Логически БД разделены: переход на отдельные серверы меняет только `DATABASE_URL`.

Векторный индекс — Qdrant, им владеет только indexing-service. retrieval-service ходит в индекс через API indexing-service, а не в Qdrant напрямую.

### Обработка ошибок
Единый формат ответа: `{"error": {"code", "message", "request_id", "details"}}`. Stack trace пишется только в лог.

| Ситуация | Код | Пример `code` |
|----------|-----|---------------|
| неверные входные данные | 400 / 422 | `validation_error`, `invalid_question`, `weak_password` |
| нет ресурса | 404 | `not_found`, `message_unknown` |
| нет токена / токен неверный или истёк | 401 | `unauthorized`, `invalid_token`, `token_expired` |
| нет прав | 403 | `forbidden` |
| конфликт состояния | 409 | `email_taken`, `sync_running`, `last_admin` |
| превышен лимит | 429 + `Retry-After` | `rate_limited` |
| соседний или внешний сервис недоступен | 502 | `upstream_error`, `llm_unavailable`, `llm_model_missing` |
| БД недоступна | 503 | `database_error` |
| таймаут соседа или LLM | 504 | `upstream_timeout`, `llm_timeout` |

Деградация вместо отказа:
- reranker недоступен → retrieval ищет без него и помечает ответ `degraded: ["reranker"]`;
- брокер недоступен → auth, chat и ingestion продолжают работать, событие пишется в лог как непубликованное.

### Логи
Каждый сервис пишет JSON в stdout: `timestamp, service, level, request_id, logger, message` и поля события (`method, path, status, duration_ms, event, user_id`…). Пробы `/health` и `/ready` в журнал запросов не пишутся.
```json
{"timestamp": "2026-10-08T05:31:07.589+00:00", "service": "chat-service", "level": "INFO", "request_id": "8e96db2d…",
 "logger": "rag_common.access", "message": "POST /api/chat/ask → 200", "method": "POST", "path": "/api/chat/ask", "status": 200, "duration_ms": 2140.3}
```

### Health checks
- `GET /health` — процесс жив (liveness);
- `GET /ready` — готовы зависимости, без которых сервис не выполняет свою работу.

| Сервис | `/ready` проверяет |
|--------|--------------------|
| auth, ingestion, chat | своя БД |
| analytics | БД и брокер (данные приходят событиями) |
| indexing | Qdrant, коллекция (нужна размерность модели от inference), брокер |
| inference | модели загружены |
| retrieval | inference и indexing отвечают |

`GET /api/status` на gateway собирает `/ready` всех сервисов.

### Веб-интерфейс
`ui/` — одна страница без сборки: HTML, CSS и JavaScript (ES-модули), nginx отдаёт файлы и проксирует `/api/*` на gateway.

| Экран | Что умеет | API |
|-------|-----------|-----|
| вход | вход и регистрация, выход; истёкший токен → снова вход, недоотправленный вопрос сохраняется | `/api/auth/*` |
| чат | ответ с форматированием, ссылки `[n]` кликабельны и подсвечивают источник, источники ведут на kubernetes.io; отказ выделен; таймер ожидания (на CPU ответ 10–20 с); ошибки 429/502/504 с `request_id` | `/api/chat/ask` |
| диалоги | список, открыть и продолжить, удалить (с подтверждением), новый диалог | `/api/chat/conversations` |
| оценка | 👍/👎 под ответом, повторная оценка заменяет прежнюю | `/api/feedback` |
| администрирование (только admin) | готовность сервисов, состояние индекса, запуск синхронизации с автообновлением, сводка аналитики и цитируемые документы | `/api/status`, `/api/indexing/status`, `/api/ingestion/runs`, `/api/analytics/summary` |

Решения:
- **Один origin.** Браузер обращается к тому же адресу, с которого загружена страница, поэтому CORS не нужен. Адрес gateway задаётся при старте контейнера переменной `GATEWAY_URL`, через шаблон nginx.
- **Безопасность.**
  - CSP разрешает только свои скрипты и запросы.
  - Ответ модели вставляется в страницу как текст (`textContent`), а не как HTML.
  - JWT хранится в `sessionStorage`, до закрытия вкладки.
  - Роль проверяют gateway и сервисы; UI только скрывает панель администратора.
- **Без сборки.** Для пяти экранов бандлер и `node_modules` не нужны. Образ — `nginx-unprivileged` (не root) плюс ≈55 КБ своих файлов, 23 МБ.

## 3. Используемые технологии и почему

| Что | Выбор | Почему | Альтернативы |
|-----|-------|--------|--------------|
| Язык, фреймворк | Python 3.12, FastAPI | код Lab1 (grabber, chunking, фильтры, генерация) переносится без переписывания; async, OpenAPI/Swagger из коробки, Pydantic-валидация | Go — быстрее, но ML-часть всё равно на Python; Spring — тяжелее для 7 небольших сервисов |
| БД | PostgreSQL 17 + SQLAlchemy 2 (async, asyncpg) | транзакции, уникальные ограничения (email, идемпотентность событий), JSON-поля для источников | MongoDB — схемы стабильны, реляционные ограничения нужнее |
| Векторная БД | Qdrant 1.19 | та же, что в Lab1 (обоснование там): фильтры по metadata, официальный образ | pgvector — меньше инфраструктуры, но хуже фильтрация и ANN |
| Брокер | RabbitMQ 4.3 | маршрутизация по типу события (topic), ack, dead letter из коробки, лёгкий для Minikube, консоль управления | Kafka — журнал и replay, но тяжелее (KRaft, больше памяти) и избыточен для нескольких событий в минуту; NATS — проще, но персистентность и DLQ сложнее |
| HTTP между сервисами | httpx (async) | таймауты, MockTransport для тестов | gRPC — быстрее, но JSON удобнее отлаживать, а нагрузка невелика |
| Auth | JWT HS256 (PyJWT), bcrypt | gateway проверяет токен без обращения к auth-service | сессии в Redis — лишний сетевой вызов; RS256 + JWKS — лучше при внешних клиентах |
| Модели | sentence-transformers, PyTorch CPU | выбор моделей — Lab1, E4/E6 | — |
| UI | HTML + CSS + JS (ES-модули) без сборки, nginx | статика и прокси в одном лёгком образе, без CORS | React/Vite (как в `old/`) — сборка и зависимости ради пяти экранов избыточны |
| LLM | Ollama на хосте (`qwen3:8b`) | выбор — Lab1, E8; GPU хоста недоступен в контейнерах Minikube | контейнер Ollama — нужен проброс GPU и 13 ГБ моделей в образ/том |

## 4. Установка

Нужны Docker с Compose v2 и [Ollama](https://ollama.com/download) на хосте с моделью:
```bash
ollama pull qwen3:8b
```

Для локальной разработки и тестов без Docker нужен Python 3.12+:
```bash
cd new/lab2
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements-dev.txt
```

## 5. Запуск

### Docker Compose
```bash
cd new/lab2
copy .env.example .env             # задать пароли, JWT_SECRET (≥ 32 символа), ADMIN_EMAIL/ADMIN_PASSWORD
docker compose up --build -d
docker compose ps                  # все сервисы healthy
```

Порядок старта задан `depends_on` и healthcheck: инфраструктура → сервисы → gateway. Снаружи открыты:
- веб-интерфейс — `http://localhost:8080`;
- gateway — `http://localhost:8000`;
- консоль RabbitMQ — `http://localhost:15672`.

Первый запуск inference-service скачивает модели (≈3.4 ГБ) в том `models`. Чтобы взять уже скачанные в Lab1, укажите `HF_CACHE=C:/Users/<you>/.cache/huggingface` и `HF_HUB_OFFLINE=1`.

Наполнение базы знаний (от имени admin):
```bash
curl -X POST localhost:8000/api/ingestion/runs -H "Authorization: Bearer $ADMIN_TOKEN"
```
Дальше всё идёт по событию: ingestion публикует `documents.changed` пачками по 50 документов, indexing индексирует их по одной. Полный корпус (6497 chunks) на CPU контейнера индексируется ≈19 мин; прогресс — `GET /api/indexing/status`. Для быстрой проверки задайте `FETCH_LIMIT=30`. Сценарий целиком — `scripts/demo.py --base-url http://localhost:8000` (пароль admin — `DEMO_ADMIN_PASSWORD`).

### Без Docker: вся система одной командой
```bash
pip install -r requirements-dev.txt
pip install torch==2.11.0 sentence-transformers==6.1.0 transformers==5.19.0 --extra-index-url https://download.pytorch.org/whl/cu128
python scripts/run_local.py            # 8 процессов; Ctrl+C — остановить (или --detach / --stop)
python scripts/demo.py                 # сценарий через gateway: auth → сбор → индекс → поиск → ответы
```
`run_local.py` запускает каждый сервис отдельным процессом uvicorn со своими переменными окружения. Отличия от Compose:

| В Compose | Без Docker |
|-----------|------------|
| PostgreSQL | SQLite: отдельный файл на сервис в `.local/`, БД по-прежнему раздельные |
| сервер Qdrant | локальный режим (`QDRANT_PATH=.local/qdrant`), как в Lab1 |
| RabbitMQ | нет: события остаются в процессе-издателе. Индекс после синхронизации обновляется `POST /api/indexing/reconcile` (`demo.py` делает это сам), analytics-service данных не получает |

Секрет JWT и пароль admin генерируются при первом запуске: `.local/secrets.json`, в git не попадает. Логи сервисов (JSON) — `.local/logs/<сервис>.log`.

### Один сервис отдельно
Каждый сервис запускается сам по себе со своим `.env` (образец — `.env.example` в папке сервиса):
```bash
cd services/auth-service
uvicorn auth_service.main:create_app --factory --port 8001
```

## 6. Configuration

Все параметры — переменные окружения, они читаются через pydantic-settings: env важнее `.env`.
- Секреты: `JWT_SECRET`, пароли БД, `GITHUB_TOKEN`, `ADMIN_PASSWORD` — только в `.env`. В git попадает `.env.example`.
- Обязательные секреты без значения → сервис не стартует: например, `JWT_SECRET` короче 32 символов отклоняется при запуске.

| Сервис | Ключевые параметры (полный список — `.env.example` сервиса) |
|--------|--------------------------------------------------------------|
| все | `LOG_LEVEL`, `RABBITMQ_URL`, `DATABASE_URL` (если есть БД) |
| auth | `JWT_SECRET`, `JWT_ALGORITHM`, `JWT_ISSUER`, `TOKEN_TTL_MINUTES`, `PASSWORD_MIN_LENGTH`, `ADMIN_EMAIL`, `ADMIN_PASSWORD` |
| ingestion | `GITHUB_REPO`, `GITHUB_REF`, `DOCS_ROOT`, `SECTIONS`, `GITHUB_TOKEN`, `MAX_WORKERS`, `FETCH_LIMIT`, `SYNC_INTERVAL_MINUTES` |
| inference | `EMBEDDING_MODEL`, `QUERY_PREFIX`, `PASSAGE_PREFIX`, `RERANKER_ENABLED`, `RERANKER_MODEL`, `DEVICE`, `MAX_TEXTS`, `MAX_CONCURRENCY` |
| indexing | `QDRANT_URL`, `CHUNK_STRATEGY`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `INCLUDE_HEADING`, `EMBED_BATCH`, `RECONCILE_ON_STARTUP`, `INGESTION_URL`, `INFERENCE_URL` |
| retrieval | `TOP_K`, `CANDIDATES`, `SCORE_THRESHOLD`, `DEDUP_THRESHOLD`, `MIN_CHARS`, `RERANKER_ENABLED`, `RERANK_MIN_SCORE`, `RERANK_FALLBACK` |
| chat | `LLM_BASE_URL`, `LLM_MODEL`, `LLM_THINK`, `LLM_TEMPERATURE`, `LLM_TIMEOUT_S`, `PROMPTS_FILE`, `PROMPT_NAME`, `RETRIEVAL_URL` |
| analytics | `TOP_SOURCES` |
| gateway | `JWT_SECRET`, `<SERVICE>_URL`, `UPSTREAM_TIMEOUT_S`, `RATE_LIMIT_PER_MINUTE`, `ROUTES_FILE` (маршруты, роли, лимиты — `gateway/routes.yaml`) |

Значения по умолчанию в `config.py` сервисов — итог экспериментов Lab1: heading-1000, e5-base, cos 0.78, rerank 0.1, top-5, `qwen3:8b`, промпт `strict`.

## 7. API

Swagger:
- gateway — `http://localhost:8000/docs`;
- каждый сервис через gateway, с кнопкой Authorize (Bearer) — `http://localhost:8000/docs/{auth|ingestion|indexing|retrieval|chat|analytics}`;
- у сервиса напрямую — `/docs` (в Compose порты сервисов не открыты наружу).

| Метод и путь | Кто | Что делает |
|--------------|-----|------------|
| `POST /api/auth/register` | все | регистрация (роль user), 201 |
| `POST /api/auth/login` | все | JWT: `{access_token, expires_in}` |
| `GET /api/auth/me` | user | текущий пользователь |
| `GET /api/auth/users`, `PATCH /api/auth/users/{id}/role` | admin | пользователи и роли |
| `POST /api/ingestion/runs` | admin | запустить синхронизацию с GitHub, 202 (409 — уже идёт) |
| `GET /api/ingestion/runs/{id}`, `GET /api/ingestion/runs` | admin | статус и статистика запусков |
| `GET /api/ingestion/documents[?section=&q=]`, `GET /api/ingestion/documents/{id}` | user | документы корпуса |
| `GET /api/indexing/status` | user | коллекция, число chunks и документов, последняя задача |
| `POST /api/indexing/reconcile` | admin | сверить индекс с корпусом, 202 |
| `POST /api/search` | user | семантический поиск: chunks, шаги фильтрации, задержки |
| `POST /api/chat/ask` | user | ответ со ссылками и источниками или отказ |
| `GET /api/chat/conversations[/{id}]`, `DELETE /api/chat/conversations/{id}` | user (свои) | история диалогов |
| `POST /api/feedback` | user (свой ответ) | оценка ответа 1 / -1 |
| `GET /api/analytics/summary[?days=]`, `GET /api/analytics/questions[?refused=&rating=]` | admin | качество системы |
| `GET /api/status` | все | готовность всех сервисов |

Источник в ответе `/api/chat/ask` (`sources[]`): `n` — номер фрагмента, `refs` — все номера `[n]` этой страницы в ответе (несколько фрагментов одной страницы дают один источник), `title`, `heading`, `url`.

## 8. Примеры использования

```bash
# вход и токен
TOKEN=$(curl -s localhost:8000/api/auth/login -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"<ADMIN_PASSWORD>"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# вопрос
curl -s localhost:8000/api/chat/ask -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"question":"Как ограничить потребление памяти контейнером?"}'
```
Ответ (живой прогон, `scripts/demo.py`):
```json
{
  "id": "…", "conversation_id": "50b06f4e-…", "refused": false, "model": "qwen3:8b", "prompt": "strict",
  "question": "Как ограничить потребление памяти контейнером?",
  "answer": "Чтобы ограничить потребление памяти контейнером, укажите `resources.limits.memory` в манифесте контейнера [2]. Это установит верхнюю границу памяти, которую контейнер может использовать. Если контейнер превысит этот лимит, ядро ОС может завершить его работу [4]. Также можно использовать `resources.requests.memory` для указания минимального объема памяти [2].",
  "sources": [
    {"n": 2, "title": "Assign Memory Resources to Containers and Pods", "url": "https://kubernetes.io/docs/tasks/configure-pod-container/assign-memory-resource/", …},
    {"n": 4, "title": "Resource Management for Pods and Containers", "url": "https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/", …}
  ],
  "stages": {"retrieved": 20, "score_threshold": 20, "dedup": 17, "min_length": 17, "rerank": 10, "final": 5},
  "timings_ms": {"retrieval": 254, "generation": 7694, "total": 7948}, "degraded": []
}
```
Вопрос вне базы («Как приготовить борщ?») → `"refused": true`, `"model": null`, 55 мс: фильтры поиска отсекли всё, LLM не вызывалась.

Ошибки в едином формате:
```text
POST /api/auth/register (повтор)  → 409 email_taken: Пользователь с таким email уже зарегистрирован
GET  /api/chat/conversations       → 401 unauthorized: Нужен заголовок Authorization: Bearer <token> (POST /api/auth/login)
POST /api/ingestion/runs (user)    → 403 forbidden: Недостаточно прав: нужна роль admin
POST /api/chat/ask (11-й за минуту) → 429 rate_limited: Не больше 10 запросов в минуту, повторите через 5 с
POST /api/search (inference упал)  → 502 upstream_error: inference-service недоступен (ConnectError)
```

## 9. Тестирование

```bash
pytest            # 97 тестов, ≈8 с: без Docker, сети, моделей и Ollama (+ 6 e2e пропускаются без E2E_BASE_URL)
```

Как устроены тесты:
- PostgreSQL заменён на SQLite (aiosqlite), Qdrant — на локальный режим в памяти, RabbitMQ — на `InMemoryEventBus`;
- соседние сервисы, GitHub и Ollama — на `httpx.MockTransport` и заглушки;
- код и HTTP-контракты сервисов — настоящие.

| Где | Что проверяется |
|-----|-----------------|
| `libs/common/tests` | JSON-лог с обязательными полями и request_id; 500 без stack trace; перевод сбоев соседа в 502/504/4xx; X-Request-ID в исходящих вызовах; сериализация событий |
| `auth-service` | регистрация, нормализация email, дубли 409, слабый пароль, JWT; одинаковая ошибка для неверного пароля и неизвестного email; 401/403; последний admin; событие без email; одновременный старт реплик (создание admin) |
| `ingestion-service` | первый и повторный запуск (инкрементальность), изменение и удаление → событие, дубли, повреждённый файл → partial и докачка, сбой источника → failed, один запуск за раз (409), права |
| `indexing-service` | 28 тестов очистки и chunking из Lab1; событие → индекс → index.updated; неизменённый документ не векторизуется заново; удаление; поиск с фильтром; сверка при старте; 503, пока модели грузятся |
| `inference-service` | эмбеддинги и rerank, лимиты запроса, 503 до загрузки моделей, выключенный reranker |
| `retrieval-service` | порядок шагов конвейера, порог reranker пустит в отказ, деградация без reranker, 502/504 соседей |
| `chat-service` | ответ с источниками из ссылок [n], отказ без вызова LLM, распознавание отказа модели, приватность диалогов, 502/504 LLM без сохранения мусора |
| `analytics-service` | сводка по событиям, идемпотентность повторной доставки, правила оценок, фильтры, права |
| `gateway` | удаление поддельных X-User-*, 401/403 до сервиса, request_id и query, лимиты 429 на маршрут и пользователя, 502/504, `/api/status`, OpenAPI через gateway, ошибка в routes.yaml |
| `tests/e2e` | сквозной сценарий против запущенной системы (пропускается без `E2E_BASE_URL`) |
| `ui/` | вручную в браузере (раздел 10): вход и ошибки входа, ответ со ссылками, отказ, история, оценки, панель admin, недоступный сервис, истёкший токен, мобильная ширина |

Сквозной тест против запущенной системы:
```bash
E2E_BASE_URL=http://localhost:8000 E2E_ADMIN_EMAIL=admin@example.com E2E_ADMIN_PASSWORD=<ADMIN_PASSWORD> pytest tests/e2e
# без RabbitMQ (scripts/run_local.py): + E2E_NO_BROKER=1 — проверки событий в analytics пропускаются
```

## 10. Результаты экспериментов
Качество ответов исследовано в Lab1: конвейер и параметры здесь те же, результаты — `../lab1/README.md`, разделы 10–11.

### Docker Compose (2026-10-08)
`docker compose up --build`: 8 образов сервисов плюс PostgreSQL 17, RabbitMQ 4.3 и Qdrant 1.19. Inference работает на CPU (PyTorch CPU в образе), Ollama — на хосте (GPU), модели взяты из кэша Lab1 (`HF_CACHE`).

| Что | Результат |
|-----|-----------|
| образы | inference 2.0 ГБ (PyTorch + модели — в томе), остальные 285–417 МБ |
| старт | все 11 контейнеров healthy, `/api/status = ok` через ≈25 с после `up` (inference грузит модели ≈20 с) |
| синхронизация с GitHub | 452 документа за 16 с → `documents.changed` в RabbitMQ |
| индексация **по событию** | indexing получил событие, 424 документа, **6497 chunks (как в Lab1)** за 18.6 мин на CPU → `index.updated` |
| пачки событий | 45 изменённых документов при `EVENT_BATCH_SIZE=20` → 3 сообщения, обработаны по одному за 24–52 с |
| сверка при старте | после удаления 45 документов из корпуса indexing при перезапуске убрал 35 лишних документов из индекса |
| ответ `/api/chat/ask` | 11.6–16.5 с: поиск ≈9.5 с (из них reranker на CPU ≈9–12.5 с), LLM 2.2–6.6 с |
| вопрос вне базы | отказ за 54 мс без вызова LLM |
| события → analytics | оценка ответа принята (`question.answered` обработан), сводка: 3 вопроса, доля отказов 0.333, последнее обновление индекса есть |
| сквозной `pytest tests/e2e` | **6 passed** |
| веб-интерфейс `web` | healthy за ≈5 с после gateway; регистрация → вопрос → ответ со ссылками и источниками (21 с — первый запрос после старта), оценка принята, диалог в истории; в логах nginx нет 4xx/5xx |
| ошибки | 0 записей ERROR в логах 8 сервисов; очереди `*.dead` пусты |
| изоляция БД | пользователь `chat` к БД `auth`: `permission denied for database "auth"` |
| трассировка через брокер | `request_id` запуска синхронизации виден в логах indexing-service при обработке события |
| память | сервисы 53–105 МБ; inference 1.26 ГБ (обе модели); PostgreSQL 60 МБ, RabbitMQ 109 МБ, Qdrant 77 МБ |

**Узкое место — reranker на CPU.** Cross-encoder `bge-reranker-v2-m3` (568M параметров) на 10–17 парах «вопрос–chunk» тратит на CPU ≈9–12.5 с против 0.34 с на GPU (прогон без Docker ниже). Индексация на CPU — 18.6 мин против 79 с. Варианты по убыванию эффекта:
1. Отдать inference-service видеокарту: Docker Desktop с WSL2 поддерживает NVIDIA GPU (`deploy.resources.reservations.devices`), но нужен образ с PyTorch CUDA (+2–3 ГБ).
2. Меньше пар для reranker: `CANDIDATES=10` вместо 20. Lab1 (E5) показала, что нужный документ почти всегда в top-5 векторного поиска.
3. `RERANKER_ENABLED=false`: поиск ≈0.1 с, но MRR и Recall multi-doc ниже (Lab1, E6: Recall@5 multi-doc 1.0 → 0.86).

Логика системы от этого не меняется; в Lab3 (Minikube, CPU) учитывается в лимитах ресурсов и таймаутах.

### Без Docker (`scripts/run_local.py`, GPU)
Пока Docker Desktop не запускался, та же система проверена отдельными процессами: SQLite вместо PostgreSQL, локальный Qdrant, без RabbitMQ, inference на GPU (RTX 4070 Ti).

| Что | Результат |
|-----|-----------|
| синхронизация / индексация | 452 документа за 18 с / 6497 chunks за 79 с |
| поиск `/api/search` | embed 48 мс + Qdrant 27 мс + reranker 338 мс |
| ответ `/api/chat/ask` | 3.0–7.9 с: поиск ≈0.25 с, остальное — LLM |
| сквозной `pytest tests/e2e` (`E2E_NO_BROKER=1`) | 4 passed, 2 skipped (события через брокер) |
| трассировка | один `request_id` в логах gateway → chat → retrieval → inference (embed, rerank) → indexing |
| rate limit | 10 вопросов в минуту → 11-й и 12-й: 429, `Retry-After: 5` |
| inference-service остановлен | `/api/search` → 502 `inference-service недоступен`; `/api/status` → 503 `inference: unreachable, retrieval: not_ready`; история диалогов работает |

Ответы в обоих прогонах совпадают с Lab1 слово в слово: тот же индекс, модели, промпт и seed. Микросервисное разделение качество не изменило. Сетевые переходы между сервисами почти ничего не стоят. В трассировке одного запроса embed занял 12 мс, поиск в индексе 19 мс, rerank 200 мс — всего 231 мс внутри сервисов. Весь `/api/search` занял 246 мс, то есть HTTP между процессами добавил ≈15 мс.

## 11. Выводы
1. **7 бизнес-сервисов с одним владельцем у каждого вида данных:** корпус — ingestion, индекс — indexing, диалоги — chat, пользователи — auth, аналитика — analytics. Чужие данные сервисы получают только через API или события; в Compose это обеспечено и правами PostgreSQL. Поэтому система одинаково поднимается и в Compose, и без Docker — простой заменой хранилищ, без правки кода сервисов.
2. **Тяжёлое отделено от лёгкого.** Модели (3.4 ГБ) живут только в inference-service; остальные сервисы — десятки МБ. В Lab3 это позволит дать ресурсы и реплики только туда, где они нужны.
3. **Синхронно — то, что нужно пользователю сейчас, асинхронно — остальное.** Ответ на вопрос идёт по REST-цепочке с таймаутами и понятными 502/504. Индексация и аналитика идут по событиям: их задержка или сбой не ломают чат. Пропущенные события догоняет сверка индекса.
   Живой прогон в Compose выявил, что событие «переиндексировать весь корпус» на CPU обрабатывается ≈19 мин — близко к `consumer_timeout` RabbitMQ (30 мин). Поэтому изменения публикуются пачками по 50 документов.
4. **Наблюдаемость с первого дня.** JSON-логи с единым `request_id` от gateway до модели позволили на живом прогоне увидеть, сколько времени занимает каждый шаг одного запроса.
5. **Ограничения:**
   - один сервер PostgreSQL на все БД (логически раздельных) — компромисс ради ресурсов;
   - rate limit gateway в памяти процесса: при нескольких репликах нужен Redis;
   - LLM — внешняя Ollama на хосте, вне оркестрации;
   - на CPU reranker делает ответ медленным (≈10 с поиска); на GPU — 0.3 с. Варианты — раздел 10.
