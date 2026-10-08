from rag_common.app import ServiceSettings


class Settings(ServiceSettings):
    service_name: str = "analytics-service"
    database_url: str = "postgresql+asyncpg://analytics:analytics@localhost:5432/analytics"
    rabbitmq_url: str | None = "amqp://guest:guest@localhost:5672/"
    events_queue: str = "analytics.events"
    top_sources: int = 10                # сколько документов в топе цитируемых
    max_comment_chars: int = 1000
