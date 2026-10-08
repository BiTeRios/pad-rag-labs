import pytest
from fastapi.testclient import TestClient
from ingestion_helpers import FakeSource

from ingestion_service.config import Settings
from ingestion_service.main import create_app
from rag_common.events import InMemoryEventBus


@pytest.fixture
def source() -> FakeSource:
    return FakeSource({
        "concepts/workloads/pods/_index.md": "---\ntitle: Pods\n---\nPods are the smallest units.",
        "concepts/services-networking/service.md": "# Service\nExpose an application.",
        "tasks/run-application/run-stateless.md": "---\ntitle: Run a Stateless App\n---\nUse a Deployment.",
    })


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus("ingestion-service")


@pytest.fixture
def client(tmp_path, source, bus):
    settings = Settings(database_url=f"sqlite+aiosqlite:///{tmp_path / 'ingestion.db'}", rabbitmq_url=None, max_workers=2)
    with TestClient(create_app(settings, event_bus=bus, source=source)) as client:
        yield client
