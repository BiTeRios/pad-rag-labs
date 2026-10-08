import pytest
from fastapi.testclient import TestClient

from inference_service.config import Settings
from inference_service.main import create_app


class FakeModels:
    """Вместо весов: вектор — длина текста, rerank — доля общих слов с вопросом."""

    def __init__(self, loaded=True, error=None):
        self.loaded, self.error, self.device, self.dim = loaded, error, "cpu", 3
        self.calls = []

    def load(self):  # загрузка «не удалась»: состояние задано в конструкторе
        pass

    def embed(self, texts, kind):
        self.calls.append((kind, texts))
        return [[float(len(text)), 0.0, 1.0] for text in texts]

    def rerank(self, query, documents):
        words = set(query.lower().split())
        return [len(words & set(doc.lower().split())) / len(words) for doc in documents]


def make_client(models, **overrides):
    return TestClient(create_app(Settings(max_texts=3, max_text_chars=50, **overrides), models=models))


@pytest.fixture
def client():
    with make_client(FakeModels()) as client:
        yield client


def test_embed_and_rerank(client):
    response = client.post("/internal/embed", json={"texts": ["pod", "service"], "kind": "query"}).json()
    assert response["dim"] == 3 and len(response["vectors"]) == 2 and response["model"] == "intfloat/multilingual-e5-base"

    scores = client.post("/internal/rerank", json={"query": "what is pod", "documents": ["pod is a unit", "cat"]}).json()
    assert scores["scores"][0] > scores["scores"][1]
    assert client.get("/internal/info").json()["loaded"] is True


def test_request_limits_and_validation(client):
    too_many = client.post("/internal/embed", json={"texts": ["a"] * 4, "kind": "passage"})
    assert too_many.status_code == 400 and too_many.json()["error"]["code"] == "too_many_texts"
    too_long = client.post("/internal/rerank", json={"query": "q", "documents": ["x" * 51]})
    assert too_long.json()["error"]["code"] == "text_too_long"
    assert client.post("/internal/embed", json={"texts": [], "kind": "query"}).status_code == 422
    assert client.post("/internal/embed", json={"texts": ["a"], "kind": "other"}).status_code == 422


def test_not_ready_until_models_loaded():
    with make_client(FakeModels(loaded=False)) as client:
        assert client.get("/health").status_code == 200  # процесс жив
        assert client.get("/ready").status_code == 503
        response = client.post("/internal/embed", json={"texts": ["a"], "kind": "query"})
        assert response.status_code == 503 and "загружаются" in response.json()["error"]["message"]

    with make_client(FakeModels(loaded=False, error="OSError: нет весов")) as client:
        assert "нет весов" in client.get("/ready").json()["checks"]["models"]


def test_reranker_can_be_disabled():
    with make_client(FakeModels(), reranker_enabled=False) as client:
        response = client.post("/internal/rerank", json={"query": "q", "documents": ["d"]})
        assert response.status_code == 409 and response.json()["error"]["code"] == "reranker_disabled"
        assert client.get("/internal/info").json()["reranker_model"] is None
