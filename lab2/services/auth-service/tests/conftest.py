import pytest
from fastapi.testclient import TestClient

from auth_service.config import Settings
from auth_service.main import create_app
from auth_helpers import ADMIN
from rag_common.events import InMemoryEventBus


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        database_url=f"sqlite+aiosqlite:///{tmp_path / 'auth.db'}", rabbitmq_url=None,
        jwt_secret="test-secret-test-secret-test-secret!", admin_email=ADMIN["email"], admin_password=ADMIN["password"],
    )


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus("auth-service")


@pytest.fixture
def client(settings, bus):
    with TestClient(create_app(settings, event_bus=bus)) as client:
        yield client
