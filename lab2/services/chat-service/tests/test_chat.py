import json

import httpx
import pytest
from fastapi.testclient import TestClient

from chat_service.config import Settings
from chat_service.generator import cited_sources
from chat_service.main import create_app
from rag_common.events import InMemoryEventBus
from rag_common.testing import as_admin, as_user

REFUSAL = "В документации недостаточно информации для ответа на этот вопрос."


def chunk(n: int, doc: str) -> dict:
    heading = f"{doc} > Section"
    return {"chunk_id": f"{doc}#{n}", "document_id": doc, "title": doc, "heading": heading, "section": "concepts",
            "url": f"https://kubernetes.io/docs/{doc}/", "text": f"{heading}\n\nText about {doc}.", "score": 0.9,
            "rerank_score": 0.9}


class Neighbours:
    def __init__(self):
        self.chunks = [chunk(0, "limits"), chunk(1, "pods")]
        self.llm_answer = "Укажите resources.limits.memory [1]."
        self.llm_status = 200
        self.llm_error: Exception | None = None
        self.retrieval_requests: list[httpx.Request] = []
        self.llm_requests: list[dict] = []

    def retrieval(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            self.retrieval_requests.append(request)
            chunks = [] if "борщ" in json.loads(request.content)["query"] else self.chunks
            return httpx.Response(200, json={"query": "q", "chunks": chunks, "degraded": [],
                                             "stages": {"final": len(chunks)}, "timings_ms": {}})
        return httpx.MockTransport(handle)

    def llm(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            if self.llm_error:
                raise self.llm_error
            self.llm_requests.append(json.loads(request.content))
            if self.llm_status != 200:
                return httpx.Response(self.llm_status, json={"error": "model not found"})
            return httpx.Response(200, json={"message": {"content": self.llm_answer}, "prompt_eval_count": 100,
                                             "eval_count": 20, "total_duration": 1_500_000_000})
        return httpx.MockTransport(handle)


@pytest.fixture
def neighbours() -> Neighbours:
    return Neighbours()


@pytest.fixture
def bus() -> InMemoryEventBus:
    return InMemoryEventBus("chat-service")


@pytest.fixture
def client(tmp_path, neighbours, bus):
    settings = Settings(database_url=f"sqlite+aiosqlite:///{tmp_path / 'chat.db'}", rabbitmq_url=None)
    app = create_app(settings, event_bus=bus, transports={"retrieval": neighbours.retrieval(), "llm": neighbours.llm()})
    with TestClient(app) as client:
        yield client


def ask(client, question="Как ограничить память контейнера?", user="u1", **body):
    return client.post("/api/chat/ask", json={"question": question, **body}, headers=as_user(user))


def test_answer_with_cited_sources_is_saved_and_published(client, neighbours, bus):
    response = ask(client)
    message = response.json()
    assert response.status_code == 200 and message["refused"] is False and message["model"] == "qwen3:8b"
    assert [source["document_id"] for source in message["sources"]] == ["limits"]  # сослался только на [1]
    assert set(message["timings_ms"]) == {"retrieval", "generation", "total"}

    request = neighbours.llm_requests[0]
    assert request["think"] is False and request["options"]["seed"] == 42
    assert "[1] limits > Section" in request["messages"][1]["content"]
    assert REFUSAL in request["messages"][0]["content"]  # фраза отказа подставлена в system prompt
    assert neighbours.retrieval_requests[0].headers["X-User-Id"] == "u1"  # личность передана дальше

    [event] = bus.of_type("question.answered")
    assert event.payload["message_id"] == message["id"] and event.payload["sources"] == ["limits"]
    assert event.payload["llm_called"] is True and event.payload["refused"] is False


def test_no_context_means_refusal_without_llm(client, neighbours, bus):
    message = ask(client, "Как приготовить борщ?").json()
    assert message["refused"] is True and message["answer"] == REFUSAL and message["sources"] == []
    assert message["model"] is None and neighbours.llm_requests == []
    assert bus.of_type("question.answered")[0].payload["llm_called"] is False


def test_model_refusal_is_detected(client, neighbours):
    neighbours.llm_answer = REFUSAL
    message = ask(client).json()
    assert message["refused"] is True and message["sources"] == []


def test_conversations_are_private(client):
    first = ask(client).json()
    second = ask(client, "А как задать requests?", conversation_id=first["conversation_id"]).json()
    assert second["conversation_id"] == first["conversation_id"]

    full = client.get(f"/api/chat/conversations/{first['conversation_id']}", headers=as_user("u1")).json()
    assert [m["question"] for m in full["messages"]] == ["Как ограничить память контейнера?", "А как задать requests?"]
    assert client.get("/api/chat/conversations", headers=as_user("u1")).json()["total"] == 1

    assert client.get(f"/api/chat/conversations/{first['conversation_id']}", headers=as_user("u2")).status_code == 404
    assert ask(client, user="u2", conversation_id=first["conversation_id"]).status_code == 404
    assert client.get(f"/api/chat/conversations/{first['conversation_id']}", headers=as_admin()).status_code == 200

    assert client.delete(f"/api/chat/conversations/{first['conversation_id']}", headers=as_user("u2")).status_code == 404
    assert client.delete(f"/api/chat/conversations/{first['conversation_id']}", headers=as_user("u1")).status_code == 204
    assert client.get("/api/chat/conversations", headers=as_user("u1")).json()["total"] == 0


@pytest.mark.parametrize(
    "setup, status, code",
    [
        (lambda n: setattr(n, "llm_error", httpx.ReadTimeout("slow")), 504, "llm_timeout"),
        (lambda n: setattr(n, "llm_error", httpx.ConnectError("refused")), 502, "llm_unavailable"),
        (lambda n: setattr(n, "llm_status", 404), 502, "llm_model_missing"),
    ],
)
def test_llm_failures_are_reported_clearly(client, neighbours, setup, status, code):
    setup(neighbours)
    response = ask(client)
    assert response.status_code == status and response.json()["error"]["code"] == code
    assert client.get("/api/chat/conversations", headers=as_user("u1")).json()["total"] == 0  # ничего не сохранено


def test_validation_and_auth(client):
    assert ask(client, "   ").json()["error"]["code"] == "invalid_question"
    assert ask(client, "x" * 1001).status_code == 400
    assert client.post("/api/chat/ask", json={"question": "q"}).status_code == 401
    assert client.get("/ready").json()["checks"] == {"database": "ok"}


def test_cited_sources_from_lab1():
    chunks = [chunk(0, "a"), chunk(1, "b"), chunk(2, "a")]
    assert [s["n"] for s in cited_sources("x [3] y [2, 1] z [9]", chunks)] == [1, 2]  # одна страница — один источник
    assert len(cited_sources("без ссылок", chunks)) == 2
