from pydantic import Field

from rag_common.app import ServiceSettings


class Settings(ServiceSettings):
    service_name: str = "auth-service"
    database_url: str = "postgresql+asyncpg://auth:auth@localhost:5432/auth"
    rabbitmq_url: str | None = "amqp://guest:guest@localhost:5672/"  # пусто — события только в лог

    jwt_secret: str = Field(min_length=32)  # обязателен: из .env / Kubernetes Secret; для HS256 ≥ 32 байт
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "rag-auth"
    token_ttl_minutes: int = 60

    password_min_length: int = 8
    # Первый администратор создаётся при старте, если его ещё нет (иначе управлять ролями некому).
    admin_email: str | None = None
    admin_password: str | None = None
