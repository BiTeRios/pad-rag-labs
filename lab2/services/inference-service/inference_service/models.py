"""Модели: bi-encoder для эмбеддингов (e5) и cross-encoder reranker (bge-reranker-v2-m3). Код из Lab1."""

import logging
import time

log = logging.getLogger(__name__)


class Models:
    def __init__(self, settings):
        self.settings = settings
        self.embedder = None
        self.reranker = None
        self.device: str | None = None
        self.error: str | None = None

    @property
    def loaded(self) -> bool:
        return self.embedder is not None and (self.reranker is not None or not self.settings.reranker_enabled)

    @property
    def dim(self) -> int | None:
        return self.embedder.get_embedding_dimension() if self.embedder else None

    def load(self) -> None:
        """Блокирующая загрузка (минуты при первом скачивании весов); вызывается в отдельном потоке."""
        try:
            import torch
            from sentence_transformers import CrossEncoder, SentenceTransformer
            from transformers.utils import logging as transformers_logging

            transformers_logging.disable_progress_bar()
            s = self.settings
            self.device = ("cuda" if torch.cuda.is_available() else "cpu") if s.device == "auto" else s.device
            started = time.perf_counter()
            embedder = SentenceTransformer(s.embedding_model, device=self.device)
            embedder.max_seq_length = s.max_seq_length
            self.embedder = embedder
            if s.reranker_enabled:
                self.reranker = CrossEncoder(s.reranker_model, max_length=s.reranker_max_length, device=self.device)
            log.info("Модели загружены на %s за %.0f с", self.device, time.perf_counter() - started,
                     extra={"embedding_model": s.embedding_model, "reranker": s.reranker_enabled})
        except Exception as error:  # noqa: BLE001 — сервис жив, /ready покажет причину
            self.error = f"{type(error).__name__}: {error}"
            log.exception("Модели не загрузились")

    def embed(self, texts: list[str], kind: str) -> list[list[float]]:
        prefix = self.settings.query_prefix if kind == "query" else self.settings.passage_prefix
        vectors = self.embedder.encode(
            [prefix + text for text in texts], batch_size=self.settings.embedding_batch_size,
            normalize_embeddings=True, convert_to_numpy=True, show_progress_bar=False,
        )
        return vectors.tolist()

    def rerank(self, query: str, documents: list[str]) -> list[float]:
        scores = self.reranker.predict(
            [(query, document) for document in documents], batch_size=self.settings.reranker_batch_size,
            show_progress_bar=False,
        )
        return [float(score) for score in scores]
