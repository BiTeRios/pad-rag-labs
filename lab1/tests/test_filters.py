import pytest

from src.reranking.reranker import Reranker
from src.retrieval import filters
from src.retrieval.pipeline import RetrievalPipeline
from tests.helpers import WordOverlapCrossEncoder, make_chunk

LONG = "pods are the smallest deployable units of computing that you can create and manage"


def scored(doc_id: str, index: int, text: str, score: float, heading: str | None = None) -> dict:
    chunk = make_chunk(doc_id, index, text, score=score)
    if heading is not None:
        chunk["heading"] = heading
        chunk["text"] = f"{heading}\n\n{text}"
    return chunk


class StubRetriever:
    """Возвращает заранее заданные chunks и запоминает параметры вызова."""

    def __init__(self, chunks: list[dict]):
        self.chunks = chunks
        self.calls: list[tuple] = []

    def retrieve(self, query, top_k=None, filters=None):
        self.calls.append((query, top_k, filters))
        return self.chunks[:top_k]


def test_by_score_threshold_and_disabled():
    chunks = [scored("a", 0, LONG, 0.9), scored("b", 0, LONG, 0.7)]
    assert [c["document_id"] for c in filters.by_score(chunks, 0.8)] == ["a"]
    assert filters.by_score(chunks, 0) == chunks


def test_min_length_ignores_heading_prefix():
    short = scored("a", 0, "See kuberc for more.", 0.9, heading="Very Long Title > With Long Section Name")
    assert filters.by_min_length([short], 50) == []
    assert filters.by_min_length([scored("b", 0, LONG, 0.9)], 50) != []


def test_deduplicate_keeps_most_relevant_of_near_duplicates():
    original = scored("a", 0, LONG, 0.9)
    near = scored("b", 0, LONG + " today", 0.85)  # почти та же формулировка на другой странице
    exact = scored("c", 0, LONG, 0.8)
    other = scored("d", 0, "services expose a set of pods as a network service", 0.7)

    result = filters.deduplicate([original, near, exact, other], threshold=0.8)

    assert [c["document_id"] for c in result] == ["a", "d"]
    assert len(filters.deduplicate([original, near, exact], threshold=1.0)) == 2  # только точные дубли
    assert len(filters.deduplicate([original, exact], threshold=0)) == 2  # выключено


def test_limit_per_document():
    chunks = [scored("a", i, f"{LONG} {i}", 0.9 - i / 10) for i in range(3)] + [scored("b", 0, LONG, 0.5)]
    assert [c["chunk_id"] for c in filters.limit_per_document(chunks, 2)] == ["a#0", "a#1", "b#0"]
    assert filters.limit_per_document(chunks, 0) == chunks


def test_reranker_reorders_by_cross_encoder_score_and_keeps_vector_score():
    model = WordOverlapCrossEncoder()
    chunks = [scored("vector-top", 0, "kubernetes cluster overview", 0.9), scored("answer", 0, "memory limit for container", 0.8)]

    ranked = Reranker("fake", model=model).rerank("memory limit container", chunks)

    assert [c["document_id"] for c in ranked] == ["answer", "vector-top"]
    assert ranked[0]["rerank_score"] == pytest.approx(1.0) and ranked[0]["score"] == 0.8
    assert model.pairs[0] == ("memory limit container", "kubernetes cluster overview")
    assert Reranker("fake", model=model).rerank("q", []) == []


def test_pipeline_takes_candidates_filters_reranks_and_cuts_top_k():
    candidates = [
        scored("noise", 0, "kubernetes cluster overview and architecture of the control plane", 0.86),
        scored("dup", 0, "memory limit for a container is set in resources limits memory field", 0.85),
        scored("dup", 1, "memory limit for a container is set in resources limits memory field", 0.84),
        scored("short", 0, "See memory.", 0.83),
        scored("answer", 0, "to set memory limit for container use resources limits memory", 0.82),
        scored("weak", 0, "memory limit container but too far from the query", 0.70),
    ]
    retriever = StubRetriever(candidates)
    pipeline = RetrievalPipeline(
        retriever,
        Reranker("fake", model=WordOverlapCrossEncoder()),
        top_k=2, candidates=20, score_threshold=0.78, dedup_threshold=0.8, min_chars=20,
        metadata={"source": "kubernetes-docs"},
    )

    result = pipeline.run("memory limit container", metadata={"section": "concepts"})

    assert retriever.calls == [("memory limit container", 20, {"source": "kubernetes-docs", "section": "concepts"})]
    assert result.stages == {
        "retrieved": 6, "score_threshold": 5, "dedup": 4, "min_length": 3, "rerank": 3, "final": 2,
    }
    assert [c["chunk_id"] for c in result.chunks] == ["dup#0", "answer#0"]
    assert all("rerank_score" in c for c in result.chunks)


def test_pipeline_without_reranker_keeps_vector_order():
    retriever = StubRetriever([scored(f"d{i}", 0, f"{LONG} {i}", 0.9 - i / 100) for i in range(8)])

    result = RetrievalPipeline(retriever, None, top_k=3, candidates=10).run("pods")

    assert [c["document_id"] for c in result.chunks] == ["d0", "d1", "d2"]
    assert "rerank" not in result.stages and retriever.calls[0][1] == 10


def test_pipeline_returns_empty_when_nothing_relevant():
    retriever = StubRetriever([scored("borsch", 0, LONG, 0.75)])
    pipeline = RetrievalPipeline(retriever, Reranker("fake", model=WordOverlapCrossEncoder()), score_threshold=0.78)

    result = pipeline.run("как приготовить борщ")

    assert result.chunks == [] and result.stages["final"] == 0


def test_rerank_min_score_drops_weak_candidates():
    retriever = StubRetriever([scored("a", 0, "memory limit container", 0.9), scored("b", 0, "unrelated text here", 0.9)])
    pipeline = RetrievalPipeline(retriever, Reranker("fake", model=WordOverlapCrossEncoder()), rerank_min_score=0.5)

    assert [c["document_id"] for c in pipeline.run("memory limit container").chunks] == ["a"]
