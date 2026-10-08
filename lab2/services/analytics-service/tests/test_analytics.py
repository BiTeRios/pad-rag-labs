import pytest
from fastapi.testclient import TestClient

from analytics_service.config import Settings
from analytics_service.main import create_app
from rag_common.events import Event, InMemoryEventBus
from rag_common.testing import as_admin, as_user


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus("chat-service")


@pytest.fixture
def client(tmp_path, bus):
    settings = Settings(database_url=f"sqlite+aiosqlite:///{tmp_path / 'analytics.db'}", rabbitmq_url=None)
    with TestClient(create_app(settings, event_bus=bus)) as client:
        yield client


def answered(client, bus, message_id: str, *, user="u1", refused=False, total=2000, sources=("limits",), degraded=()):
    client.portal.call(bus.publish, "question.answered", {
        "message_id": message_id, "conversation_id": "c1", "user_id": user, "question": f"вопрос {message_id}",
        "refused": refused, "llm_called": not refused, "sources": list(sources), "model": "qwen3:8b",
        "prompt": "strict", "timings_ms": {"retrieval": 300, "generation": total - 300, "total": total},
        "degraded": list(degraded),
    })


def test_events_build_summary(client, bus):
    answered(client, bus, "m1", total=1000, sources=("limits", "pods"))
    answered(client, bus, "m2", total=3000, sources=("limits",), degraded=("reranker",))
    answered(client, bus, "m3", refused=True, sources=())
    client.portal.call(bus.publish, "user.registered", {"user_id": "u1", "role": "user"})
    client.portal.call(bus.publish, "index.updated", {"trigger": "event", "added": 452, "updated": 0, "deleted": 0,
                                                      "chunks_indexed": 6497, "duration_s": 61.5, "collection": "k8s"})

    summary = client.get("/api/analytics/summary", headers=as_admin()).json()
    assert summary["questions"] == 3 and summary["refusal_rate"] == pytest.approx(0.333, abs=1e-3)
    assert summary["degraded_rate"] == pytest.approx(0.333, abs=1e-3)
    assert summary["latency_ms"] == {"mean": 2000, "p95": 3000}  # только ответы с вызовом LLM
    assert summary["top_sources"][0] == {"document_id": "limits", "citations": 2}
    assert summary["users_registered"] == 1 and summary["last_index_update"]["chunks_indexed"] == 6497


def test_redelivered_event_is_counted_once(client, bus):
    event = Event("question.answered", {"message_id": "m1", "user_id": "u1", "question": "q", "refused": False,
                                        "sources": [], "timings_ms": {"total": 1}})
    projector_handler = client.app.state.event_bus._subscriptions[0].handler
    client.portal.call(projector_handler, event)
    client.portal.call(projector_handler, event)  # та же доставка второй раз (at-least-once)
    assert client.get("/api/analytics/summary", headers=as_admin()).json()["questions"] == 1


def test_feedback_rules(client, bus):
    answered(client, bus, "m1", user="u1")
    created = client.post("/api/feedback", json={"message_id": "m1", "rating": -1, "comment": "неполно"}, headers=as_user("u1"))
    assert created.status_code == 201 and created.json()["created"] is True
    updated = client.post("/api/feedback", json={"message_id": "m1", "rating": 1}, headers=as_user("u1"))
    assert updated.status_code == 200 and updated.json()["created"] is False

    assert client.post("/api/feedback", json={"message_id": "m1", "rating": 1}, headers=as_user("u2")).status_code == 403
    unknown = client.post("/api/feedback", json={"message_id": "nope", "rating": 1}, headers=as_user("u1"))
    assert unknown.status_code == 404 and unknown.json()["error"]["code"] == "message_unknown"
    assert client.post("/api/feedback", json={"message_id": "m1", "rating": 5}, headers=as_user("u1")).status_code == 422

    summary = client.get("/api/analytics/summary", headers=as_admin()).json()
    assert summary["feedback"] == {"count": 1, "positive": 1, "negative": 0, "positive_rate": 1.0}


def test_questions_listing_filters(client, bus):
    answered(client, bus, "m1")
    answered(client, bus, "m2", refused=True)
    client.post("/api/feedback", json={"message_id": "m1", "rating": -1}, headers=as_user("u1"))

    refused = client.get("/api/analytics/questions", params={"refused": True}, headers=as_admin()).json()
    assert [row["message_id"] for row in refused] == ["m2"]
    negative = client.get("/api/analytics/questions", params={"rating": -1}, headers=as_admin()).json()
    assert [row["message_id"] for row in negative] == ["m1"] and negative[0]["rating"] == -1


def test_admin_only_and_ready(client):
    assert client.get("/api/analytics/summary", headers=as_user()).status_code == 403
    assert client.get("/api/analytics/summary").status_code == 401
    empty = client.get("/api/analytics/summary", headers=as_admin()).json()
    assert empty["questions"] == 0 and empty["refusal_rate"] is None and empty["last_index_update"] is None
    assert client.get("/ready").json()["status"] == "ready"
