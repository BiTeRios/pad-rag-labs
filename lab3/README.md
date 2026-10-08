# Lab3. Docker и Kubernetes: RAG-система из Lab2 в Minikube

## 1. Описание проекта

Приложение из Lab2 упаковано в образы и развёрнуто в Kubernetes (Minikube). Состав приложения:
- RAG по документации Kubernetes: вопросы на русском, ответы со ссылками;
- 7 бизнес-сервисов и API Gateway;
- PostgreSQL, RabbitMQ, Qdrant.

| Что | Где |
|-----|-----|
| Dockerfile каждого сервиса | `../lab2/services/<service>/Dockerfile`, `../lab2/gateway/Dockerfile`: лежат рядом с кодом сервиса, источник один |
| Docker Compose (проверка перед Kubernetes) | `../lab2/docker-compose.yml` |
| Сборка образов и загрузка в Minikube | `docker/build_images.py` |
| Манифесты Kubernetes | `k8s/`: namespace, Deployments, StatefulSets, Services, ConfigMaps, Secret, PVC |
| Secret со случайными паролями | `scripts/make_secret.py` (в git только шаблон) |
| Демонстрация для защиты | `scripts/demo.py` |

Ни код сервисов, ни образы под Kubernetes не менялись. Всё, что отличает окружение (адреса соседей, пароли, параметры моделей), приходит из ConfigMap и Secret. Для Kubernetes в Lab2 сделаны две правки:
- у образов в Compose общие теги `rag/<service>:1.0.0`;
- одновременный старт нескольких реплик auth-service больше не конфликтует при создании администратора (тест `test_replica_starts_when_admin_was_created_concurrently`).

## 2. Архитектура

```text
 хост (Windows)                      Minikube: узел minikube, namespace rag
 ───────────────                     ────────────────────────────────────────────────────────────────────────────
 браузер ──:8080──►  Service web (NodePort 30081) ──► Deployment web ×2 (nginx: статика, /api → gateway)
 kubectl port-forward ──:8000──►  Service gateway (NodePort 30080) ──► Deployment gateway ×2
                                         │ http://<service>:<port> (DNS-имена Service, не localhost)
           ┌──────────────┬──────────────┼───────────────┬───────────────┬────────────────┐
           ▼              ▼              ▼               ▼               ▼                ▼
     auth-service ×2  ingestion ×1  indexing ×1    retrieval ×2     chat ×2         analytics ×1
           │              │          │      │        │      │         │   │              │
           │              │          │      └──► inference ×1 ◄──┘    │   └─► Ollama на хосте (GPU):
           │              │          │      e5 + reranker, PVC        │       host.minikube.internal:11434
           ▼              ▼          ▼      inference-models 8Gi      ▼              ▼
     ┌──────────────── postgres-0 (StatefulSet, PVC 1Gi): БД auth · ingestion · chat · analytics ──────────┐
     │                 qdrant-0   (StatefulSet, PVC 2Gi): векторный индекс (только indexing)               │
     └──────────────── rabbitmq-0 (StatefulSet, PVC 1Gi): события rag.events ─────────────────────────────┘
 ConfigMap rag-common + <service>-config → envFrom          Secret rag-secrets → secretKeyRef (по ключу)
```

### Объекты Kubernetes

| Компонент | Объект | Реплик | Service | Порт | Probes: liveness / readiness | requests → limits | Хранилище |
|-----------|--------|-------:|---------|-----:|------------------------------|-------------------|-----------|
| gateway | Deployment | 2 | NodePort 30080 | 8000 | `/health` / `/ready` | 50m, 96Mi → 500m, 256Mi | — |
| web (UI) | Deployment | 2 | NodePort 30081 | 8080 | `/healthz` / `/healthz` | 10m, 16Mi → 200m, 64Mi | — |
| auth-service | Deployment | 2 | ClusterIP | 8001 | `/health` / `/ready` (БД) | 50m, 96Mi → 500m, 256Mi | БД `auth` |
| ingestion-service | Deployment, Recreate | 1 | ClusterIP | 8002 | `/health` / `/ready` (БД) | 50m, 128Mi → 1, 512Mi | БД `ingestion` |
| inference-service | Deployment, Recreate | 1 | ClusterIP | 8003 | `/health` / `/ready` (модели загружены) | 1, 2Gi → 6, 4Gi | PVC `inference-models` |
| indexing-service | Deployment, Recreate | 1 | ClusterIP | 8004 | `/health` / `/ready` (Qdrant, брокер, коллекция) | 100m, 192Mi → 1, 768Mi | Qdrant |
| retrieval-service | Deployment | 2 | ClusterIP | 8005 | `/health` / `/ready` (inference, indexing) | 50m, 96Mi → 500m, 256Mi | — |
| chat-service | Deployment | 2 | ClusterIP | 8006 | `/health` / `/ready` (БД) | 50m, 96Mi → 500m, 256Mi | БД `chat` |
| analytics-service | Deployment | 1 | ClusterIP | 8007 | `/health` / `/ready` (БД, брокер) | 50m, 96Mi → 250m, 256Mi | БД `analytics` |
| postgres | StatefulSet | 1 | headless | 5432 | `pg_isready` | 100m, 128Mi → 1, 512Mi | PVC 1Gi |
| rabbitmq | StatefulSet | 1 | headless | 5672, 15672 | `rabbitmq-diagnostics ping` / TCP 5672 | 100m, 256Mi → 1, 768Mi | PVC 1Gi |
| qdrant | StatefulSet | 1 | headless | 6333 | `/livez` / `/readyz` | 100m, 256Mi → 1, 1Gi | PVC 2Gi |

### Решения и почему

**Deployment и StatefulSet.**
- Сервисы приложения не хранят состояние в поде, поэтому это Deployment.
- PostgreSQL, RabbitMQ и Qdrant — StatefulSet. У пода стабильное имя (`postgres-0`) и свой том из `volumeClaimTemplates`; после пересоздания под получает тот же том.
- Для RabbitMQ стабильное имя обязательно: каталог данных привязан к имени узла `rabbit@rabbitmq-0`.

**Реплики.**
- По 2 реплики у сервисов без внутреннего состояния (gateway, auth, retrieval, chat): отказ одного пода не прерывает работу.
- ingestion и indexing — ровно одна реплика со стратегией `Recreate`. Синхронизация, задача индексации и сверка индекса защищены блокировкой внутри процесса. Две копии во время rolling update начали бы обрабатывать одно и то же параллельно.
- inference — одна реплика: каждая копия занимает 2+ ГБ памяти и все выделенные ядра. Масштабировать её имеет смысл только вместе с ресурсами узла.

**Service.**
- Сервисы приложения доступны через ClusterIP по DNS-имени: `http://retrieval-service:8005`. kube-proxy распределяет соединения по готовым подам.
- У StatefulSet — headless Service (`clusterIP: None`): имя `postgres` указывает прямо на под `postgres-0`.
- Наружу открыт только gateway (NodePort). Пути `/internal/*` извне недоступны: gateway их не проксирует, а ClusterIP не виден с хоста.

**ConfigMap и Secret.**
- Параметры лежат в ConfigMap, а не в образе: адреса соседей, хосты БД и брокера, модели, chunking, top-K, пороги, LLM, промпт, лимиты.
- Пароли и JWT-секрет лежат в Secret. Каждый сервис получает через `secretKeyRef` только свои ключи: chat-service не знает пароль БД `auth`.
- `DATABASE_URL` собирается в Deployment из двух источников: `postgresql+asyncpg://chat:$(DB_PASSWORD)@$(DATABASE_HOST):$(DATABASE_PORT)/chat`. Хост и порт берутся из ConfigMap, пароль — из Secret. `kubectl describe pod` показывает шаблон, а не пароль.

**Probes.**
- liveness `/health` отвечает: «процесс жив». Если она не проходит, kubelet перезапускает контейнер.
- readiness `/ready` проверяет зависимости сервиса: БД, брокер, загружены ли модели, отвечают ли соседи. Пока она не проходит, под исключён из Service и трафик на него не идёт, но контейнер не перезапускается.
- У inference-service `/ready` становится зелёным только после загрузки моделей (первый старт — скачивание 3.4 ГБ). Поэтому liveness там с запасом: под нагрузкой ответ может задерживаться.

**Ресурсы.**
- requests и limits выставлены по замерам из Compose: сервисы занимают 50–110 МиБ, inference — 1.3–1.9 ГиБ.
- Число потоков PyTorch равно limit по CPU. Оно передаётся через Downward API: `OMP_NUM_THREADS ← limits.cpu`. Без этого PyTorch запустил бы потоки по числу ядер узла и упёрся бы в квоту CPU.

**Безопасность подов.**
- `runAsNonRoot`, uid 10001, как `USER app` в Dockerfile.
- `allowPrivilegeEscalation: false`, все capabilities сброшены, профиль seccomp `RuntimeDefault`.
- `enableServiceLinks: false`: Kubernetes не добавляет переменные вида `RABBITMQ_PORT=tcp://…`, которые конфликтуют с настройками сервисов и образа RabbitMQ.

### Docker

| Образ | Размер | Что внутри |
|-------|-------:|------------|
| `rag/inference-service:1.0.0` | 2.01 GB | PyTorch CPU (без CUDA), sentence-transformers |
| `rag/indexing-service:1.0.0` | 417 MB | preprocessing Lab1, qdrant-client |
| `rag/ingestion-service:1.0.0` | 307 MB | grabber Lab1 |
| `rag/auth-service:1.0.0` | 304 MB | bcrypt, PyJWT |
| `rag/chat-service:1.0.0`, `rag/analytics-service:1.0.0` | 303 MB | — |
| `rag/gateway:1.0.0`, `rag/retrieval-service:1.0.0` | 285 MB | — |
| `rag/web:1.0.0` | 23 MB | `nginx-unprivileged` (uid 101) + статика UI, без сборки |

Чем оптимизированы Dockerfile (пример — `../lab2/services/inference-service/Dockerfile`):
- база `python:3.12-slim`; `PIP_NO_CACHE_DIR`, без компиляторов;
- `requirements.txt` копируется и устанавливается **до кода**: при правке кода слой с зависимостями берётся из кэша;
- PyTorch ставится с CPU-индекса: колесо ≈200 МБ вместо ≈2.5 ГБ с CUDA (плюс библиотеки NVIDIA), в Minikube GPU всё равно нет;
- `.dockerignore`: контекст — корень lab2, в образ не попадают `.venv`, тесты, `.env`, кэши, документация;
- секретов в образе нет: всё приходит из env (Compose `.env`, Kubernetes Secret);
- процесс работает не от root: `USER app` (uid 10001);
- CMD в exec-форме (`uvicorn … --factory`), поэтому сигнал SIGTERM от Kubernetes получает сам uvicorn и завершает работу корректно.

## 3. Используемые технологии

| Что | Выбор | Почему | Альтернативы |
|-----|-------|--------|--------------|
| Кластер | Minikube 1.39, driver docker, Kubernetes 1.37, containerd | один узел в Docker Desktop, без VM; требование задания | kind (без addons и `minikube service`), k3d, Kubernetes в Docker Desktop |
| Сборка манифестов | kustomize (`kubectl apply -k`) | встроен в kubectl; namespace создаётся первым, подкаталоги собираются одним списком | `kubectl apply -R -f` (нет порядка: ресурсы падают, пока нет namespace), Helm (шаблоны избыточны для одного окружения) |
| Образы в кластер | `minikube image load` | сборка на хосте с кэшем слоёв, тот же образ, что в Compose | `minikube docker-env` (сборка внутри узла заново), локальный registry |
| Данные | StatefulSet + PVC (StorageClass `standard`, hostpath) | данные переживают пересоздание подов и `minikube stop` | PostgreSQL/RabbitMQ вне кластера, операторы (CloudNativePG, RabbitMQ Operator) |
| Доступ снаружи | Service NodePort + `kubectl port-forward` | работает с любым драйвером Minikube | Ingress (addon ingress-nginx): нужен для нескольких хостов/TLS, здесь вход один |
| LLM | Ollama на хосте (GPU) | в Minikube нет GPU; qwen3:8b на CPU отвечала бы минуты | Ollama в кластере (CPU), GPU passthrough в Minikube |

## 4. Установка

Нужно:
- Docker Desktop;
- [minikube](https://minikube.sigs.k8s.io/docs/start/) ≥ 1.39;
- kubectl: лучше той же версии, что кластер; подойдёт и `minikube kubectl --`;
- Python ≥ 3.10 для скриптов (только стандартная библиотека);
- Ollama на хосте с моделью `qwen3:8b` (`ollama pull qwen3:8b`).

Ресурсы Minikube:
- 8 CPU и 10 ГБ памяти: inference занимает до 6 ядер и 4 ГБ, остальное — около 3 ГБ;
- диск ≈10 ГБ: образы ≈4.5 ГБ, модели 3.4 ГБ, данные.

## 5. Запуск

```bash
cd lab3
minikube start --driver=docker --cpus=8 --memory=10g
python docker/build_images.py              # 9 образов: docker build (кэш) + minikube image load
python scripts/make_secret.py              # k8s/secrets/secret.yaml со случайными паролями (в .gitignore)
kubectl apply -k k8s/                      # namespace, ConfigMap, Secret, PVC, StatefulSet, Deployment, Service
kubectl config set-context --current --namespace=rag   # дальше kubectl get pods без -n rag
kubectl get pods -w                        # все 1/1 Running
kubectl port-forward svc/gateway 8000:8000 # API и Swagger: http://localhost:8000/docs
kubectl port-forward svc/web 8080:8080     # веб-интерфейс: http://localhost:8080 (в другом окне)
```

Через NodePort без port-forward: `minikube service gateway -n rag --url`. На Windows и macOS с драйвером docker команда держит туннель, пока открыта.

Первый запуск:
1. Поды поднимаются примерно за минуту.
2. inference-service скачивает модели в свой том и становится Ready через 1.5–2 мин.
3. Корпус собирается по запросу администратора. Пароль admin: `kubectl get secret rag-secrets -o jsonpath='{.data.ADMIN_PASSWORD}' | base64 -d`.
   ```bash
   TOKEN=$(curl -s localhost:8000/api/auth/login -H 'Content-Type: application/json' \
     -d '{"email":"admin@example.com","password":"<пароль>"}' | jq -r .access_token)
   curl -X POST localhost:8000/api/ingestion/runs -H "Authorization: Bearer $TOKEN"
   ```
4. ingestion публикует `documents.changed`, indexing строит индекс. Ход — в `GET /api/indexing/status`. На CPU это ≈20 мин, но только один раз: индекс хранится в томе Qdrant.

Остановка и удаление:
- `minikube stop` / `minikube start` — данные и индекс сохраняются в томах.
- `kubectl delete -k k8s/` — удаляет приложение. Тома StatefulSet (`data-postgres-0` и др.) остаются, том моделей удаляется.
- `minikube delete` — удаляет кластер целиком.

Обновить сервис после правки кода:
```bash
python docker/build_images.py chat-service && kubectl rollout restart deployment/chat-service
```

## 6. Configuration

Сервисы читают настройки только из переменных окружения (pydantic-settings, как в Lab2). В Kubernetes переменные приходят из следующих объектов.

| Объект | Ключи | Кто читает |
|--------|-------|------------|
| ConfigMap `rag-common` (`k8s/configmaps/common.yaml`) | `LOG_LEVEL`; `DATABASE_HOST/PORT`, `RABBITMQ_HOST/PORT/USER`, `QDRANT_URL`; `AUTH_URL` … `ANALYTICS_URL` | все (`envFrom`) |
| ConfigMap `auth-config` | `TOKEN_TTL_MINUTES`, `PASSWORD_MIN_LENGTH` | auth |
| ConfigMap `ingestion-config` | `GITHUB_REPO`, `SECTIONS`, `FETCH_LIMIT`, `EVENT_BATCH_SIZE`, `SYNC_INTERVAL_MINUTES` | ingestion |
| ConfigMap `inference-config` | `EMBEDDING_MODEL`, `RERANKER_ENABLED`, `RERANKER_MODEL`, `DEVICE`, `HF_HUB_OFFLINE` | inference |
| ConfigMap `indexing-config` | `CHUNK_STRATEGY`, `CHUNK_SIZE`, `CHUNK_OVERLAP`, `EMBED_BATCH`, `INFERENCE_TIMEOUT_S` | indexing |
| ConfigMap `retrieval-config` | `TOP_K`, `CANDIDATES`, `SCORE_THRESHOLD`, `RERANKER_ENABLED`, `RERANK_MIN_SCORE` | retrieval |
| ConfigMap `chat-config` | `LLM_BASE_URL`, `LLM_MODEL`, `PROMPT_NAME`, `LLM_TIMEOUT_S` | chat |
| ConfigMap `gateway-config` | `RATE_LIMIT_PER_MINUTE`, `UPSTREAM_TIMEOUT_S` | gateway |
| ConfigMap `web-config` | `GATEWAY_URL` (`http://gateway:8000`) — куда nginx проксирует `/api` | web |
| ConfigMap `postgres-init` | скрипт `init-databases.sh`: БД и пользователь на сервис | postgres (один раз) |
| Secret `rag-secrets` | `POSTGRES_PASSWORD`, `<AUTH/INGESTION/CHAT/ANALYTICS>_DB_PASSWORD`, `RABBITMQ_PASSWORD`, `JWT_SECRET`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `GITHUB_TOKEN` | каждый — только свои ключи |

Изменить параметр, например отключить reranker:
```bash
# k8s/configmaps/services.yaml: RERANKER_ENABLED: "false" в retrieval-config
kubectl apply -k k8s/ && kubectl rollout restart deployment/retrieval-service
```

Pod не перечитывает ConfigMap, подключённый через env. Поэтому после изменения нужен `rollout restart`: Deployment по очереди заменит поды, не прерывая работу (`maxUnavailable: 0`).

Secret в git не попадает:
- `k8s/secrets/secret.yaml` указан в `.gitignore`;
- в репозитории только `secret.example.yaml` с ненастоящими значениями.

В объекте Secret значения хранятся в base64, а это не шифрование. Защита держится на RBAC; в продакшене ещё шифруют etcd или используют внешнее хранилище (Vault, Sealed Secrets).

## 7. API

API приложения то же, что в Lab2 (`../lab2/README.md`, раздел 7). Вход один — gateway:
- Swagger gateway: `http://localhost:8000/docs`;
- Swagger сервисов через gateway: `http://localhost:8000/docs/{auth|ingestion|indexing|retrieval|chat|analytics}`;
- готовность всех сервисов: `GET /api/status` (агрегирует `/ready` через DNS-имена Service).

## 8. Примеры использования: демонстрация на защите

Весь сценарий из задания одной командой: `python scripts/demo.py`. Тот же сценарий по шагам:

```bash
kubectl get pods                       # 1. все поды Running, READY 1/1
kubectl get services                   # 2. ClusterIP у сервисов, NodePort у gateway, headless у БД
kubectl get deployments                # 3. READY 2/2, 1/1 …
kubectl logs deploy/chat-service       # 4. JSON-логи (timestamp, service, level, request_id, message)
kubectl logs -l app=auth-service --prefix --tail 5   #    логи всех реплик с именем пода

# 5. API через gateway (kubectl port-forward svc/gateway 8000:8000)
curl localhost:8000/api/status
curl -X POST localhost:8000/api/chat/ask -H "Authorization: Bearer $TOKEN" \
     -H 'Content-Type: application/json' -d '{"question": "Как ограничить потребление памяти контейнером?"}'

# 6. Масштабирование
kubectl scale deployment auth-service --replicas=3
kubectl get pods -l app=auth-service   # три пода; запросы распределяются между ними

# 7. Восстановление
kubectl delete pod <auth-service-…>
kubectl get pods -l app=auth-service   # вместо удалённого уже создаётся новый (ReplicaSet держит 3)
```

`scripts/demo.py` проходит этот сценарий целиком за ≈30 с: показывает ресурсы, делает запросы через gateway и прослеживает один `request_id` по подам. Затем масштабирует auth-service до 3 реплик, считает, какой под обслужил каждый из 30 параллельных запросов, удаляет под и возвращает число реплик.

## 9. Тестирование

```bash
../lab2/.venv/Scripts/python -m pytest tests        # 32 теста манифестов, ≈1 с, без кластера
kubectl apply -k k8s/ --dry-run=server              # проверка схемы API-сервером
```

`tests/test_manifests.py` проверяет то, что `kubectl apply` пропустит молча.
- Веб-интерфейс: порт совпадает с `listen` в шаблоне nginx, probes `/healthz`, uid 101 как в образе, `GATEWAY_URL` указывает на Service gateway.
- Каждый ключ ConfigMap и каждая переменная в `env` совпадает с полем `Settings` сервиса: тест импортирует код из Lab2. Опечатка вроде `RERANK_ENABLED` не прошла бы, а сервис молча взял бы значение по умолчанию.
- `containerPort` совпадает с портом uvicorn из `CMD` в Dockerfile.
- Service выбирает поды своего Deployment и ссылается на именованный порт контейнера.
- `$(VAR)` в `DATABASE_URL` определена раньше; `secretKeyRef` ссылается на существующий ключ Secret.
- У каждого Deployment есть образ с версией (не `latest`), probes `/health` и `/ready`, requests и limits по CPU и памяти, non-root.
- Адреса соседей — DNS-имена существующих Service, `localhost` нет; секретных ключей в ConfigMap нет; `secret.yaml` указан в `.gitignore`.

Против развёрнутого кластера:
```bash
kubectl port-forward svc/gateway 8000:8000
E2E_BASE_URL=http://localhost:8000 E2E_ADMIN_EMAIL=admin@example.com E2E_ADMIN_PASSWORD=<из Secret> \
  pytest ../lab2/tests/e2e          # сквозной сценарий Lab2, включая события через RabbitMQ
python ../lab2/scripts/demo.py --base-url http://localhost:8000   # сбор корпуса → индекс → поиск → ответы → аналитика
python scripts/demo.py              # сценарий защиты (раздел 8)
```

## 10. Результаты экспериментов

Прогон 2026-10-08: Minikube 1.39, Kubernetes 1.37, containerd, 8 CPU и 10 ГБ на узел (Ryzen 5 5600, Docker Desktop WSL2). LLM — Ollama на хосте с GPU.

| Что | Результат |
|-----|-----------|
| сборка и загрузка образов | `python docker/build_images.py`: 8 образов за 84 с (сборка из кэша, `minikube image load`; inference 2 ГБ — 32 с) |
| `kubectl apply -k k8s/` | 34 объекта; **все 15 подов Running и READY за ≈60 с, 0 перезапусков** |
| веб-интерфейс (добавлен позже) | `kubectl apply -k k8s/` → 2 пода `web` Ready за 6 с, остальные поды не перезапускались; через `port-forward svc/web`: вход, вопрос → ответ со ссылками (14.5 с), история диалогов, оценки, панель admin (синхронизация из UI: 452 без изменений за 1 с) |
| inference, первый старт | модели скачаны в PVC (3.2 ГБ) и загружены за 97 с; до этого под NotReady, трафик на него не шёл |
| синхронизация корпуса | 452 документа из GitHub за 18 с → 10 событий `documents.changed` по 50 документов |
| индексация **по событиям** | 424 документа, **6497 chunks (как в Lab1 и Compose)** за 18.2 мин на CPU; пачка — ≈2 мин; очередь обработана по одному сообщению (prefetch=1) |
| поиск `/api/search` | embed 40 мс, Qdrant 11 мс, reranker 9.3 с (CPU) |
| ответ `/api/chat/ask` | 10.3–15.6 с (поиск 8.3–9.4 с, LLM 2.0–6.2 с), ответ со ссылками [n] и источниками; вне базы — отказ за 49 мс без LLM |
| сквозной `pytest ../lab2/tests/e2e` | **6 passed** за 37 с (включая события через RabbitMQ → analytics) |
| трассировка | один `request_id` в логах подов gateway → chat → retrieval → inference (embed, rerank) |
| масштабирование | `kubectl scale deployment auth-service --replicas=3`: новый под Ready за 6 с; 30 параллельных запросов — 200, распределены по трём подам (10/14/6) |
| восстановление | `kubectl delete pod auth-service-…` → новый под Ready через ≈6 с, запросы не прерывались (остальные реплики в Service) |
| StatefulSet | `kubectl delete pod postgres-0` → новый под Ready за несколько секунд с тем же томом: пользователи, диалоги и аналитика на месте, сервисы переподключились без перезапусков |
| PVC моделей | `kubectl delete pod` inference → Ready за 21 с: модели из тома за 8 с, без скачивания |
| память (crictl stats) | сервисы 56–118 МБ, inference 2.0 ГБ; PostgreSQL 41 МБ, RabbitMQ 106 МБ, Qdrant 27 МБ — в пределах limits |
| ошибки | ERROR только в первые 40 с: RabbitMQ ещё не готов, его headless-имя не резолвится, сервисы переподключаются; за 23 мин работы — 0; очереди `*.dead` пусты |

**Наблюдение про балансировку.**
- Service распределяет **соединения**, а не запросы.
- gateway держит keep-alive соединения к auth-service. После масштабирования старые соединения остаются у старых подов, а новый под получает трафик только по новым соединениям.
- Повторный прогон после того, как пул уже прогрелся, дал распределение 1/18/11.
- Для равномерного распределения по запросам нужен L7-балансировщик (service mesh, Ingress) или ограничение времени жизни соединений в клиенте.

**CPU вместо GPU.** Как и в Compose, медленнее всего работают reranker (≈9 с на запрос) и первичная индексация (18 мин против 79 с на GPU). Это учтено в манифестах:
- inference получает 6 ядер и `OMP_NUM_THREADS=6`;
- таймауты retrieval → inference и chat → retrieval увеличены через ConfigMap;
- liveness inference терпит задержки под нагрузкой.

Ускорить можно так же, как в Lab2 (раздел 10): `CANDIDATES=10` или `RERANKER_ENABLED=false` в `retrieval-config`, либо узел с GPU.

## 11. Выводы

1. **Один образ — разные окружения.** Те же образы `rag/<service>:1.0.0` работают в Compose и в Kubernetes. Разница только в конфигурации: адреса, пароли и параметры приходят из ConfigMap и Secret, код под кластер не менялся. Lab3 выявила одну гонку, которой не было в Compose: две реплики auth-service одновременно создавали администратора. Это исправлено в Lab2 и покрыто тестом.
2. **Kubernetes сам поддерживает нужное состояние.**
   - удалённый под пересоздаётся за секунды, а остальные реплики за Service продолжают обслуживать запросы;
   - readiness не пускает трафик на inference, пока модели не загружены, и на сервис, у которого недоступна БД;
   - StatefulSet с PVC сохраняет данные PostgreSQL, Qdrant и веса моделей при пересоздании подов.
3. **Реплики — по природе сервиса, а не одинаково всем.** Сервисы без состояния — по 2 реплики, масштабируются одной командой. ingestion и indexing — одна реплика с `Recreate`: их задачи защищены блокировкой в процессе. inference масштабируется только вместе с ресурсами узла. Ресурсы выставлены по замерам: вся система с запасом укладывается в 10 ГБ узла.
4. **Безопасность по умолчанию:**
   - секреты только в Secret, каждый сервис видит только свои ключи, в git — только шаблон;
   - поды без root и без лишних capabilities;
   - наружу открыт только gateway.
5. **Ограничения:**
   - один узел Minikube, поэтому реплики не защищают от отказа узла;
   - PostgreSQL, RabbitMQ и Qdrant — по одной реплике, без репликации данных;
   - LLM вне кластера (Ollama на хосте);
   - rate limit gateway считается в каждой реплике отдельно, для общего лимита нужен Redis;
   - Secret в etcd не зашифрован (base64).

   Для продакшена нужны:
   - несколько узлов и операторы для БД (CloudNativePG, RabbitMQ Cluster Operator);
   - Ingress с TLS;
   - HPA по метрикам (addon metrics-server);
   - внешнее хранилище секретов;
   - узел с GPU для inference.