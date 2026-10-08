"""Retriever: query → embedding → поиск в Qdrant → top-K chunks со score."""

from src.embeddings.embedder import Embedder
from src.retrieval.vector_store import QdrantStore


class Retriever:
    def __init__(self, embedder: Embedder, store: QdrantStore, top_k: int = 5):
        self.embedder = embedder
        self.store = store
        self.top_k = top_k

    def retrieve(self, query: str, top_k: int | None = None, filters: dict | None = None) -> list[dict]:
        """filters — точное совпадение полей metadata, например {"section": "concepts/workloads/pods"}."""
        vector = self.embedder.embed_query(query)
        return self.store.search(vector, top_k or self.top_k, filters)
