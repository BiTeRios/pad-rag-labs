import time

import pytest
from fastapi.testclient import TestClient
from indexing_helpers import FakeNeighbours, bag_of_words, make_document, publish
from qdrant_client import AsyncQdrantClient

from indexing_service.config import Settings
from indexing_service.main import create_app
from rag_common.events import InMemoryEventBus
from rag_common.testing import as_admin, as_user

PODS = "concepts/workloads/pods/_index.md"
SERVICE = "concepts/services-networking/service.md"
STUB = "tasks/stub.md"
DOCUMENTS = [
    make_document(PODS, "# Pods\n\nA Pod is the smallest deployable unit of computing in Kubernetes."),
    make_document(SERVICE, "# Service\n\nA Service exposes an application running on a set of Pods over the network."),
    make_document(STUB, "---\ntitle: Stub\n---\n"),  # после очистки пусто
]


@pytest.fixture
def neighbours() -> FakeNeighbours:
    return FakeNeighbours(DOCUMENTS)


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus("ingestion-service")


def make_client(neighbours, bus, reconcile_on_startup=False):
    settings = Settings(rabbitmq_url=None, reconcile_on_startup=reconcile_on_startup, embed_batch=2)
    app = create_app(settings, event_bus=bus, qdrant=AsyncQdrantClient(location=":memory:"),
                     transports={"ingestion": neighbours.ingestion(), "inference": neighbours.inference()})
    return TestClient(app)


@pytest.fixture
def client(neighbours, bus):
    with make_client(neighbours, bus) as client:
        yield client


def status(client) -> dict:
    return client.get("/api/indexing/status", headers=as_user()).json()


def test_documents_changed_event_indexes_and_publishes_index_updated(client, bus):
    publish(client, bus, "documents.changed", {"run_id": "r1", "changed": [PODS, SERVICE, STUB], "deleted": []})

    state = status(client)
    assert state["collection"] == "k8s__test-e5__heading-1000-0-h"
    assert state["documents"] == 2 and state["points"] >= 2
    assert state["last_job"]["stats"] == {"added": 2, "updated": 0, "unchanged": 0, "deleted": 0, "empty": 1,
                                          "chunks_indexed": state["points"]}
    [event] = bus.of_type("index.updated")
    assert event.payload["run_id"] == "r1" and event.payload["added"] == 2 and event.payload["trigger"] == "event"


def test_reindexing_is_incremental(client, bus, neighbours):
    publish(client, bus, "documents.changed", {"changed": [PODS, SERVICE], "deleted": []})
    embedded = neighbours.embedded

    publish(client, bus, "documents.changed", {"changed": [PODS], "deleted": []})  # тот же текст
    assert status(client)["last_job"]["stats"]["unchanged"] == 1 and neighbours.embedded == embedded

    neighbours.put(make_document(PODS, "# Pods\n\nPods run containers. Updated text."))
    publish(client, bus, "documents.changed", {"changed": [PODS], "deleted": [SERVICE]})
    stats = status(client)["last_job"]["stats"]
    assert (stats["updated"], stats["deleted"]) == (1, 1) and status(client)["documents"] == 1


def test_document_missing_in_ingestion_is_treated_as_deleted(client, bus, neighbours):
    publish(client, bus, "documents.changed", {"changed": [PODS, SERVICE], "deleted": []})
    del neighbours.documents[SERVICE]
    publish(client, bus, "documents.changed", {"changed": [SERVICE], "deleted": []})
    assert status(client)["documents"] == 1


def test_search_returns_nearest_chunks_with_filters(client, bus):
    publish(client, bus, "documents.changed", {"changed": [PODS, SERVICE], "deleted": []})
    vector = bag_of_words("service exposes application network")

    points = client.post("/internal/search", json={"vector": vector, "limit": 2}).json()["points"]
    assert points[0]["document_id"] == SERVICE and points[0]["score"] > points[1]["score"]
    assert {"text", "heading", "url", "chunk_id", "doc_sha"} <= set(points[0])

    filtered = client.post("/internal/search", json={"vector": vector, "limit": 5,
                                                     "filters": {"section": "concepts/workloads/pods"}}).json()
    assert {p["document_id"] for p in filtered["points"]} == {PODS}
    assert client.post("/internal/search", json={"vector": vector, "limit": 1000}).status_code == 400


def test_reconcile_on_startup_catches_up_with_corpus(neighbours, bus):
    with make_client(neighbours, bus, reconcile_on_startup=True) as client:
        deadline = time.monotonic() + 5
        while (status(client)["last_job"] or {}).get("status") != "succeeded" and time.monotonic() < deadline:
            time.sleep(0.02)
        state = status(client)
        assert state["documents"] == 2 and state["last_job"]["trigger"] == "startup"


def test_manual_reconcile_is_admin_only(client):
    assert client.post("/api/indexing/reconcile", headers=as_user()).status_code == 403
    assert client.post("/api/indexing/reconcile", headers=as_admin()).status_code == 202
    assert client.get("/api/indexing/status").status_code == 401


def test_not_ready_while_inference_loads_models(neighbours, bus):
    neighbours.models_loaded = False
    with make_client(neighbours, bus) as client:
        ready = client.get("/ready")
        assert ready.status_code == 503 and "загружает модели" in ready.json()["checks"]["index"]
        search = client.post("/internal/search", json={"vector": [0.1] * 16, "limit": 1})
        assert search.status_code == 503
