from rag_common.app import ServiceSettings


class Settings(ServiceSettings):
    service_name: str = "indexing-service"
    rabbitmq_url: str | None = "amqp://guest:guest@localhost:5672/"
    events_queue: str = "indexing.documents-changed"

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None
    qdrant_path: str | None = None     # локальный режим Qdrant (папка) — запуск без сервера, как в Lab1
    # Коллекция: <prefix>__<модель>__<strategy>-<size>-<overlap>-<h|nh>; смена модели или chunking → новая коллекция
    collection_prefix: str = "k8s"

    ingestion_url: str = "http://localhost:8002"
    inference_url: str = "http://localhost:8003"
    ingestion_timeout_s: float = 30
    inference_timeout_s: float = 120   # векторизация пачки chunks на CPU

    # Chunking выбран в Lab1 (E1–E3)
    chunk_strategy: str = "heading"
    chunk_size: int = 1000
    chunk_overlap: int = 0
    include_heading: bool = True

    fetch_batch: int = 50              # документов за запрос к ingestion-service
    embed_batch: int = 64              # chunks за запрос к inference-service
    reconcile_on_startup: bool = True  # сверить индекс с корпусом при старте (пропущенные события)
    max_search_limit: int = 100
