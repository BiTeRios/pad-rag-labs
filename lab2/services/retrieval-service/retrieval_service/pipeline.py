"""Поиск контекста (логика Lab1, src/retrieval/pipeline.py); модели и индекс — соседние сервисы.

```text
вопрос ─► inference: вектор ─► indexing: top-N ─► порог cos ─► дубли ─► длина
       ─► inference: reranker ─► порог rerank ─► лимит на документ ─► top-K
```
Пустой результат — в базе нет достаточно релевантного контекста.
"""

import logging
import time
from dataclasses import dataclass, field

from retrieval_service import filters
from rag_common.errors import AppError, UpstreamError, UpstreamTimeout
from rag_common.http import ServiceClient

log = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    chunks: list[dict]
    stages: dict[str, int] = field(default_factory=dict)  # сколько chunks осталось после каждого шага
    timings_ms: dict[str, float] = field(default_factory=dict)
    degraded: list[str] = field(default_factory=list)      # какие шаги пропущены из-за сбоя соседей


class RetrievalPipeline:
    def __init__(self, inference: ServiceClient, indexing: ServiceClient, settings):
        self.inference = inference
        self.indexing = indexing
        self.s = settings

    async def run(self, query: str, top_k: int | None = None, where: dict | None = None) -> RetrievalResult:
        s = self.s
        top_k = top_k or s.top_k
        result = RetrievalResult([])
        clock = _Clock(result.timings_ms)

        embedded = await self.inference.post("/internal/embed", json={"texts": [query], "kind": "query"})
        clock.mark("embed")
        found = await self.indexing.post("/internal/search", json={
            "vector": embedded["vectors"][0], "limit": max(s.candidates, top_k), "filters": where or None})
        clock.mark("search")
        chunks = found["points"]
        result.stages["retrieved"] = len(chunks)

        chunks = filters.by_score(chunks, s.score_threshold)
        result.stages["score_threshold"] = len(chunks)
        chunks = filters.deduplicate(chunks, s.dedup_threshold)
        result.stages["dedup"] = len(chunks)
        chunks = filters.by_min_length(chunks, s.min_chars)
        result.stages["min_length"] = len(chunks)

        if s.reranker_enabled and chunks:
            chunks = await self._rerank(query, chunks, result)
            clock.mark("rerank")

        result.chunks = filters.limit_per_document(chunks, s.max_per_document)[:top_k]
        result.stages["final"] = len(result.chunks)
        return result

    async def _rerank(self, query: str, chunks: list[dict], result: RetrievalResult) -> list[dict]:
        try:
            response = await self.inference.post(
                "/internal/rerank", json={"query": query, "documents": [chunk["text"] for chunk in chunks]})
        except AppError as error:
            # сбой или таймаут inference, модели грузятся, reranker выключен — можно продолжить без него;
            # прочие 4xx — ошибка в запросе, её не маскируем
            recoverable = isinstance(error, (UpstreamError, UpstreamTimeout)) or error.code == "reranker_disabled"
            if not (self.s.rerank_fallback and recoverable):
                raise
            log.warning("Reranker недоступен (%s): порядок векторного поиска", error.message)
            result.degraded.append("reranker")
            return chunks
        ranked = sorted(
            ({**chunk, "rerank_score": score} for chunk, score in zip(chunks, response["scores"], strict=True)),
            key=lambda chunk: chunk["rerank_score"], reverse=True,
        )
        ranked = filters.by_score(ranked, self.s.rerank_min_score, key="rerank_score")
        result.stages["rerank"] = len(ranked)
        return ranked


class _Clock:
    def __init__(self, timings: dict):
        self.timings = timings
        self.last = time.perf_counter()

    def mark(self, stage: str) -> None:
        now = time.perf_counter()
        self.timings[stage] = round((now - self.last) * 1000, 1)
        self.last = now
