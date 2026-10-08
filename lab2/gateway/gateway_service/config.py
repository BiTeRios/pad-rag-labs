from pathlib import Path

from pydantic import Field

from rag_common.app import ServiceSettings

ROOT = Path(__file__).resolve().parent.parent


class Settings(ServiceSettings):
    service_name: str = "gateway"
    routes_file: Path = ROOT / "routes.yaml"

    # Адреса сервисов: в Compose и Kubernetes — DNS-имена сервисов
    auth_url: str = "http://localhost:8001"
    ingestion_url: str = "http://localhost:8002"
    inference_url: str = "http://localhost:8003"
    indexing_url: str = "http://localhost:8004"
    retrieval_url: str = "http://localhost:8005"
    chat_url: str = "http://localhost:8006"
    analytics_url: str = "http://localhost:8007"

    jwt_secret: str = Field(min_length=32)   # тот же, что у auth-service (Kubernetes Secret)
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "rag-auth"

    upstream_timeout_s: float = 30
    rate_limit_per_minute: int = 120         # на пользователя (по токену) или на IP; 0 — выкл
    max_body_bytes: int = 1_000_000

    def service_urls(self) -> dict[str, str]:
        return {name: getattr(self, f"{name}_url")
                for name in ("auth", "ingestion", "inference", "indexing", "retrieval", "chat", "analytics")}
