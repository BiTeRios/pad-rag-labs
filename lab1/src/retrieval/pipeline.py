"""Полный поиск контекста: vector search → порог → дубли → длина → reranker → лимиты → top-K.

```text
вопрос ─► Retriever (top-N кандидатов) ─► similarity threshold ─► дедупликация ─► min length
       ─► reranker (опционально, порог rerank_score) ─► не больше M chunks на документ ─► top-K
```
"""

from dataclasses import dataclass, field

from src.reranking.reranker import Reranker
from src.retrieval import filters
from src.retrieval.retriever import Retriever


@dataclass
class RetrievalResult:
    chunks: list[dict]
    stages: dict[str, int] = field(default_factory=dict)  # сколько chunks осталось после каждого шага


class RetrievalPipeline:
    def __init__(
        self,
        retriever: Retriever,
        reranker: Reranker | None = None,
        *,
        top_k: int = 5,
        candidates: int = 20,
        score_threshold: float = 0.0,
        dedup_threshold: float = 0.0,
        min_chars: int = 0,
        rerank_min_score: float = 0.0,
        max_per_document: int = 0,
        metadata: dict | None = None,
    ):
        self.retriever = retriever
        self.reranker = reranker
        self.top_k = top_k
        self.candidates = candidates
        self.score_threshold = score_threshold
        self.dedup_threshold = dedup_threshold
        self.min_chars = min_chars
        self.rerank_min_score = rerank_min_score
        self.max_per_document = max_per_document
        self.metadata = metadata or {}

    def run(self, query: str, top_k: int | None = None, metadata: dict | None = None) -> RetrievalResult:
        """Пустой результат означает, что в базе нет достаточно релевантного контекста."""
        top_k = top_k or self.top_k
        where = {**self.metadata, **(metadata or {})} or None
        # Кандидатов берётся больше top_k, чтобы после фильтров осталось из чего выбирать.
        chunks = self.retriever.retrieve(query, max(self.candidates, top_k), where)
        stages = {"retrieved": len(chunks)}

        chunks = filters.by_score(chunks, self.score_threshold)
        stages["score_threshold"] = len(chunks)
        chunks = filters.deduplicate(chunks, self.dedup_threshold)
        stages["dedup"] = len(chunks)
        chunks = filters.by_min_length(chunks, self.min_chars)
        stages["min_length"] = len(chunks)

        if self.reranker is not None:
            chunks = self.reranker.rerank(query, chunks)
            chunks = filters.by_score(chunks, self.rerank_min_score, key="rerank_score")
            stages["rerank"] = len(chunks)

        chunks = filters.limit_per_document(chunks, self.max_per_document)[:top_k]
        stages["final"] = len(chunks)
        return RetrievalResult(chunks, stages)
