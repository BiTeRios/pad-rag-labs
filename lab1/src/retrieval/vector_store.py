"""Хранилище векторов на Qdrant: одна коллекция на комбинацию модели и параметров chunking.

В Lab1 Qdrant работает в локальном режиме (данные в папке), в Lab2/3 тот же код
подключается к серверу Qdrant в контейнере.
"""

import uuid
from typing import Iterable

import numpy as np
from qdrant_client import QdrantClient, models

_SCROLL_BATCH = 1000


class QdrantStore:
    def __init__(self, client: QdrantClient, collection: str):
        self.client = client
        self.collection = collection

    def ensure_collection(self, dim: int) -> None:
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                self.collection,
                vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )

    def exists(self) -> bool:
        return self.client.collection_exists(self.collection)

    def count(self) -> int:
        return self.client.count(self.collection, exact=True).count

    def indexed_documents(self) -> dict[str, str | None]:
        """{document_id: doc_fingerprint} для всего, что уже лежит в коллекции."""
        documents: dict[str, str | None] = {}
        offset = None
        while True:
            points, offset = self.client.scroll(
                self.collection,
                limit=_SCROLL_BATCH,
                offset=offset,
                with_payload=["document_id", "doc_fingerprint"],
                with_vectors=False,
            )
            for point in points:
                documents[point.payload["document_id"]] = point.payload.get("doc_fingerprint")
            if offset is None:
                return documents

    def clear(self) -> None:
        """Удаляет все точки. Коллекция не пересоздаётся: в локальном режиме qdrant-client 1.19
        после delete_collection + create_collection с тем же именем старые точки возвращаются."""
        if self.exists():
            self.client.delete(self.collection, points_selector=models.FilterSelector(filter=models.Filter()))

    def delete_documents(self, document_ids: Iterable[str]) -> None:
        ids = list(document_ids)
        if ids:
            self.client.delete(
                self.collection,
                points_selector=models.FilterSelector(filter=_match("document_id", ids)),
            )

    def upsert(self, chunks: list[dict], vectors: np.ndarray) -> None:
        points = [
            models.PointStruct(id=point_id(chunk["chunk_id"]), vector=vector.tolist(), payload=chunk)
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        self.client.upsert(self.collection, points=points)

    def search(self, vector: np.ndarray, top_k: int, filters: dict | None = None) -> list[dict]:
        """Ближайшие chunks: payload + score (косинусная близость)."""
        query_filter = None
        if filters:
            query_filter = models.Filter(must=[_condition(key, value) for key, value in filters.items()])
        response = self.client.query_points(
            self.collection,
            query=vector.tolist(),
            limit=top_k,
            query_filter=query_filter,
            with_payload=True,
        )
        return [{**point.payload, "score": point.score} for point in response.points]


def point_id(chunk_id: str) -> str:
    """Детерминированный UUID: повторная индексация того же chunk перезаписывает точку."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def _condition(key: str, value) -> models.FieldCondition:
    if isinstance(value, (list, tuple, set)):
        return models.FieldCondition(key=key, match=models.MatchAny(any=list(value)))
    return models.FieldCondition(key=key, match=models.MatchValue(value=value))


def _match(key: str, values: list[str]) -> models.Filter:
    return models.Filter(must=[_condition(key, values)])
