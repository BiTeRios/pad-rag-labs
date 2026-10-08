# RAG по документации Kubernetes: от прототипа до микросервисов в Kubernetes

Три последовательные лабораторные работы над одной системой: вопросы на русском по англоязычной документации Kubernetes, ответы со ссылками на источники и отказ, когда в документации ответа нет.

| Лабораторная | Что сделано | README |
|--------------|-------------|--------|
| **Lab1. RAG-система** | grabber документации из GitHub (инкрементально, без дублей), очистка и chunking, эмбеддинги `multilingual-e5-base`, Qdrant, reranker `bge-reranker-v2-m3`, фильтры, генерация через Ollama (`qwen3:8b`), evaluation на 40 вопросах с LLM-судьёй, исследования E1–E9 | [lab1/README.md](lab1/README.md) |
| **Lab2. Микросервисы** | 7 бизнес-сервисов (auth, ingestion, inference, indexing, retrieval, chat, analytics) + API Gateway; REST и события RabbitMQ; БД на сервис в PostgreSQL; JWT; JSON-логи со сквозным request_id; Docker Compose | [lab2/README.md](lab2/README.md) |
| **Lab3. Docker и Kubernetes** | оптимизированные образы, манифесты Kubernetes (Deployment, StatefulSet, Service, ConfigMap, Secret, PVC, probes, resources), запуск в Minikube, масштабирование и восстановление подов | [lab3/README.md](lab3/README.md) |

## Архитектура

```text
клиент ──► API Gateway ──► auth · ingestion · indexing · retrieval · chat · analytics
                                   │           │          │          │
                         GitHub ◄──┘    Qdrant ◄┘   inference ◄┘     └──► Ollama (LLM)
                                    (e5 + reranker)
           PostgreSQL (БД на сервис) · RabbitMQ (documents.changed, index.updated, question.answered)
```

Конвейер ответа:
1. Вопрос векторизуется (e5-base).
2. Поиск выбирает 20 кандидатов в Qdrant.
3. Кандидаты фильтруются: порог 0.78, почти-дубли, короткие chunks.
4. Reranker отбирает top-5.
5. LLM отвечает только по найденным фрагментам, со ссылками `[n]`.

Параметры выбраны экспериментами Lab1 и хранятся в конфигурации: `lab1/configs/*.yaml`, env, ConfigMap.

## Структура

```text
├── README.md
├── lab1/   src/{grabber, preprocessing, embeddings, retrieval, reranking, generation, evaluation}, configs/, experiments/, tests/
├── lab2/   gateway/, services/<7 сервисов>/, libs/common/, infrastructure/, tests/, docs/, docker-compose.yml
└── lab3/   docker/, k8s/{namespace.yaml, deployments, services, statefulsets, configmaps, secrets, storage}, scripts/, tests/
```

## Технологии

Python 3.12–3.14, FastAPI, sentence-transformers / PyTorch, Qdrant, Ollama, PostgreSQL 17, RabbitMQ 4, SQLAlchemy (async), httpx, PyJWT, pytest, Docker, Docker Compose, Kubernetes (Minikube), kustomize. Почему выбрано именно это, с альтернативами — в README каждой лабораторной (раздел 3).

## Быстрый старт

Нужны Python, Docker Desktop и [Ollama](https://ollama.com) с моделью `qwen3:8b`; для Lab3 — ещё minikube.

```bash
# Lab1: собрать корпус, построить индекс, задать вопрос
cd lab1 && pip install -r requirements.txt
python -m src.ingest
python -m src.generation "Как ограничить потребление памяти контейнером?"

# Lab2: вся система одной командой (пароли — в .env)
cd lab2 && cp .env.example .env && docker compose up --build

# Lab3: Kubernetes
cd lab3 && minikube start --cpus=8 --memory=10g
python docker/build_images.py && python scripts/make_secret.py
kubectl apply -k k8s/ && kubectl port-forward -n rag svc/gateway 8000:8000
```

Подробные шаги, конфигурация, API и примеры — в README лабораторных (разделы 4–8).

## Тестирование

| Где | Команда | Тестов |
|-----|---------|-------:|
| lab1 | `pytest` | 109 |
| lab2 | `pytest` (+ `tests/e2e` против запущенной системы) | 97 + 6 e2e |
| lab3 | `python -m pytest tests` (проверка манифестов) | 30 |

## Результаты

| Что | Результат |
|-----|-----------|
| Retrieval (Lab1, 40 вопросов) | Hit@5 0.969, MRR 0.901; reranker поднял Recall@5 на multi-doc вопросах с 0.86 до 1.0 |
| Ответы (Lab1, LLM-судья) | вопросы вне базы — 100% отказов, ложных отказов 0%; correctness 0.78, faithfulness 0.98; citation hit 0.94 |
| Lab2, Docker Compose | 11 контейнеров healthy; индексация 6497 chunks по событию RabbitMQ; e2e 6/6 |
| Lab3, Minikube | 15 подов READY за ≈60 с; e2e 6/6; scale до 3 реплик и пересоздание удалённого пода за ≈6 с; данные PostgreSQL и Qdrant переживают пересоздание подов |

Подробно, вместе с выводами по каждому эксперименту, — в разделах 10–11 README лабораторных.

## Выводы

- **Качество RAG определяет retrieval.** Reranker и порог отсечения дали больше, чем смена LLM. Строгий промпт с обязательными ссылками убрал ответы «из головы».
- **Сервисы выделены по владельцу данных и по ресурсам.** У корпуса, индекса, диалогов и пользователей свой владелец. Тяжёлые модели — отдельный сервис. Синхронно идёт только то, что нужно пользователю сейчас, остальное — событиями.
- **Один образ работает во всех окружениях.** Без Docker, в Compose и в Kubernetes различается только конфигурация.
