"""Cross-encoder reranker.

Bi-encoder (embedding-модель) сравнивает заранее посчитанные векторы: это быстро, но вопрос и
текст не «видят» друг друга. Cross-encoder читает пару (вопрос, chunk) целиком и точнее
оценивает релевантность, но медленнее. Поэтому он применяется только к top-N кандидатам.
"""

import logging

log = logging.getLogger(__name__)


class Reranker:
    def __init__(
        self,
        model_name: str,
        max_length: int = 512,
        batch_size: int = 32,
        device: str = "auto",
        model=None,  # готовая модель (в тестах); иначе загружается CrossEncoder
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.model = model if model is not None else _load_model(model_name, max_length, device)

    def rerank(self, query: str, chunks: list[dict]) -> list[dict]:
        """Chunks по убыванию rerank_score (0..1); исходный score векторного поиска сохраняется."""
        if not chunks:
            return []
        scores = self.model.predict(
            [(query, chunk["text"]) for chunk in chunks],
            batch_size=self.batch_size,
            show_progress_bar=False,
        )
        ranked = [{**chunk, "rerank_score": float(score)} for chunk, score in zip(chunks, scores, strict=True)]
        return sorted(ranked, key=lambda chunk: chunk["rerank_score"], reverse=True)


def _load_model(model_name: str, max_length: int, device: str):
    from sentence_transformers import CrossEncoder

    from src.embeddings.embedder import resolve_device

    device = resolve_device(device)
    log.info("Загрузка reranker %s на %s", model_name, device)
    return CrossEncoder(model_name, max_length=max_length, device=device)
