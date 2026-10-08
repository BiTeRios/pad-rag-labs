from rag_common.app import ServiceSettings
from rag_common.settings import CommaList


class Settings(ServiceSettings):
    service_name: str = "ingestion-service"
    database_url: str = "postgresql+asyncpg://ingestion:ingestion@localhost:5432/ingestion"
    rabbitmq_url: str | None = "amqp://guest:guest@localhost:5672/"

    # Источник: документация Kubernetes в GitHub (как в Lab1)
    github_repo: str = "kubernetes/website"
    github_ref: str = "main"
    docs_root: str = "content/en/docs"
    sections: CommaList = ["concepts", "tasks", "tutorials"]
    extensions: CommaList = [".md"]
    site_url: str = "https://kubernetes.io/docs"
    source_name: str = "kubernetes-docs"
    github_token: str | None = None   # без токена — 60 запросов к API в час

    http_timeout_s: float = 30
    max_retries: int = 3
    backoff_s: float = 1.0
    max_workers: int = 8              # параллельные загрузки файлов
    fetch_limit: int = 0              # не больше N файлов за запуск (отладка); 0 — без лимита
    # documents.changed публикуется пачками: обработка одного сообщения на CPU укладывается в минуты,
    # а не упирается в consumer_timeout RabbitMQ (30 мин) при полной переиндексации
    event_batch_size: int = 50
    sync_interval_minutes: int = 0    # периодическая синхронизация; 0 — только по запросу admin
