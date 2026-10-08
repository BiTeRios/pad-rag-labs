import json

import httpx
import pytest
from fastapi.testclient import TestClient

from retrieval_service import filters
from retrieval_service.config import Settings
from retrieval_service.main import create_app
from rag_common.testing import as_user

LONG = "pods are the smallest deployable units of computing that you can create and manage in kubernetes"


def point(doc_id: str, index: int, text: str, score: float, section: str = "concepts") -> dict:
    heading = f"{doc_id} > Part {index}"
    return {"chunk_id": f"{doc_id}#{index}", "document_id": doc_id, "title": doc_id, "heading": heading,
            "url": f"https://kubernetes.io/docs/{doc_id}/", "section": section, "text": f"{heading}\n\n{text}",
            "score": score, "doc_sha": "s", "chunk_index": index}


class Neighbours:
    def __init__(self, points: list[dict]):
        self.points = points
        self.rerank_status = 200
        self.rerank_error = None
        self.search_requests: list[dict] = []
        self.search_delay_error: Exception | None = None

    def inference(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            body = json.loads(request.content)
            if request.url.path == "/internal/embed":
                return httpx.Response(200, json={"vectors": [[0.1, 0.2]], "model": "e5", "dim": 2, "duration_ms": 1})
            if self.rerank_status != 200:
                return httpx.Response(self.rerank_status, json={"error": self.rerank_error or {"code": "x", "message": "x"}})
            words = set(body["query"].lower().split())
            scores = [len(words & set(doc.lower().split())) / len(words) for doc in body["documents"]]
            return httpx.Response(200, json={"scores": scores, "model": "reranker", "duration_ms": 1})
        return httpx.MockTransport(handle)

    def indexing(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            if self.search_delay_error:
                raise self.search_delay_error
            body = json.loads(request.content)
            self.search_requests.append(body)
            return httpx.Response(200, json={"collection": "c", "points": self.points[: body["limit"]]})
        return httpx.MockTransport(handle)


@pytest.fixture
def neighbours() -> Neighbours:
    return Neighbours([
        point("pods", 0, LONG, 0.86),
        point("pods", 1, LONG, 0.85),  # дубль по тексту
        point("limits", 0, "set memory limit for a container with resources limits memory " + LONG, 0.83),
        point("short", 0, "See X.", 0.82),  # короче min_chars
        point("weak", 0, LONG + " weak", 0.70),  # ниже порога косинуса
    ])


def make_client(neighbours, **overrides):
    app = create_app(Settings(**overrides),
                     transports={"inference": neighbours.inference(), "indexing": neighbours.indexing()})
    return TestClient(app)


@pytest.fixture
def client(neighbours):
    with make_client(neighbours) as client:
        yield client


def search(client, query="memory limit container pods", **body):
    return client.post("/api/search", json={"query": query, **body}, headers=as_user())


def test_pipeline_applies_filters_and_reranker_in_order(client, neighbours):
    response = search(client).json()
    assert response["stages"] == {"retrieved": 5, "score_threshold": 4, "dedup": 3, "min_length": 2, "rerank": 2, "final": 2}
    assert [c["document_id"] for c in response["chunks"]] == ["limits", "pods"]  # reranker поднял limits
    assert response["chunks"][0]["rerank_score"] > response["chunks"][1]["rerank_score"]
    assert response["degraded"] == [] and set(response["timings_ms"]) == {"embed", "search", "rerank"}
    assert neighbours.search_requests[0]["limit"] == 20  # кандидатов больше, чем top_k


def test_rerank_threshold_can_empty_the_context(client):
    response = search(client, "борщ рецепт").json()  # ни одного общего слова → rerank 0 < 0.1
    assert response["chunks"] == [] and response["stages"]["final"] == 0


def test_section_filter_and_top_k_are_passed(client, neighbours):
    search(client, top_k=1, section="concepts/workloads")
    assert neighbours.search_requests[-1]["filters"] == {"section": "concepts/workloads"}
    assert len(search(client, top_k=1).json()["chunks"]) == 1
    assert search(client, top_k=50).json()["error"]["code"] == "invalid_top_k"
    assert search(client, "   ").json()["error"]["code"] == "invalid_query"


@pytest.mark.parametrize("status, error", [(503, None), (409, {"code": "reranker_disabled", "message": "off"})])
def test_reranker_failure_degrades_instead_of_failing(neighbours, status, error):
    neighbours.rerank_status, neighbours.rerank_error = status, error
    with make_client(neighbours) as client:
        response = search(client).json()
    assert response["degraded"] == ["reranker"] and [c["document_id"] for c in response["chunks"]] == ["pods", "limits"]


def test_reranker_failure_is_an_error_without_fallback(neighbours):
    neighbours.rerank_status = 500
    with make_client(neighbours, rerank_fallback=False) as client:
        response = search(client)
    assert response.status_code == 502 and response.json()["error"]["code"] == "upstream_error"


def test_indexing_timeout_and_outage_map_to_504_and_502(neighbours):
    neighbours.search_delay_error = httpx.ReadTimeout("slow")
    with make_client(neighbours) as client:
        timeout = search(client)
        neighbours.search_delay_error = httpx.ConnectError("refused")
        outage = search(client)
    assert timeout.status_code == 504 and "indexing-service" in timeout.json()["error"]["message"]
    assert outage.status_code == 502 and "Traceback" not in outage.text


def test_requires_identity_and_ready_checks_neighbours(client):
    assert client.post("/api/search", json={"query": "pod"}).status_code == 401
    ready = client.get("/ready").json()
    assert set(ready["checks"]) == {"inference", "indexing"}


def test_filters_from_lab1():
    chunks = [point("a", 0, LONG, 0.9), point("b", 0, LONG, 0.7)]
    assert [c["document_id"] for c in filters.by_score(chunks, 0.8)] == ["a"]
    assert filters.by_score(chunks, 0) == chunks
    assert len(filters.deduplicate(chunks, 0.8)) == 1 and len(filters.deduplicate(chunks, 0)) == 2
    assert filters.limit_per_document([point("a", 0, LONG, 0.9), point("a", 1, "x " + LONG, 0.8)], 1)[0]["chunk_id"] == "a#0"
