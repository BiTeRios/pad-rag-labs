"""Обёртка над sentence-transformers: префиксы query/passage, батчи, нормализация векторов."""

import logging

import numpy as np

log = logging.getLogger(__name__)


class Embedder:
    def __init__(
        self,
        model_name: str,
        query_prefix: str = "",
        passage_prefix: str = "",
        max_seq_length: int | None = None,
        batch_size: int = 64,
        device: str = "auto",
        model=None,  # готовая модель (в тестах); иначе загружается SentenceTransformer
    ):
        self.model_name = model_name
        self.query_prefix = query_prefix
        self.passage_prefix = passage_prefix
        self.batch_size = batch_size
        if model is None:
            model = _load_model(model_name, device)
        self.model = model
        if max_seq_length:
            self.model.max_seq_length = max_seq_length

    @property
    def dim(self) -> int:
        return self.model.get_embedding_dimension()

    def embed_documents(self, texts: list[str], show_progress: bool = False) -> np.ndarray:
        return self._encode([self.passage_prefix + text for text in texts], show_progress)

    def embed_query(self, text: str) -> np.ndarray:
        return self._encode([self.query_prefix + text], show_progress=False)[0]

    def _encode(self, texts: list[str], show_progress: bool) -> np.ndarray:
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=True,  # косинусная близость = скалярное произведение
            convert_to_numpy=True,
            show_progress_bar=show_progress,
        )


def resolve_device(device: str) -> str:
    """auto → cuda, если есть GPU, иначе cpu. Заодно отключает прогресс-бар загрузки весов."""
    import torch
    from transformers.utils import logging as transformers_logging

    transformers_logging.disable_progress_bar()
    if device == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    return device


def release_gpu_memory() -> None:
    """Вернуть драйверу видеопамять удалённых моделей (эмбеддер, reranker) перед запуском LLM в Ollama.

    Иначе на 12 GB карте эмбеддер + reranker + gemma3:12b заполняют память почти целиком (11.3 GB),
    и LLM работает заметно медленнее: судья ≈23 с на ответ против 6–16 с без них.
    """
    import gc

    import torch

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


def _load_model(model_name: str, device: str):
    from sentence_transformers import SentenceTransformer

    device = resolve_device(device)
    log.info("Загрузка embedding-модели %s на %s", model_name, device)
    return SentenceTransformer(model_name, device=device)
