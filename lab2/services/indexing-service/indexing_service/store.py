"""Векторный индекс в Qdrant (сервер). Логика из Lab1 (src/retrieval/vector_store.py), клиент — асинхронный."""

import uuid

from qdrant_client import AsyncQdrantClient, models

_SCROLL_BATCH = 1000
_KEYWORD_FIELDS = ("document_id", "section")  # индексы payload для фильтров и удаления по документу


class VectorStore:
    def __init__(self, client: AsyncQdrantClient):
        self.client = client
        self.collection: str | None = None

    async def ensure_collection(self, name: str, dim: int) -> None:
        if not await self.client.collection_exists(name):
            await self.client.create_collection(
                name, vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
            )
            for field in _KEYWORD_FIELDS:
                await self.client.create_payload_index(name, field, models.PayloadSchemaType.KEYWORD)
        self.collection = name

    async def count(self) -> int:
        return (await self.client.count(self.collection, exact=True)).count

    async def indexed_documents(self) -> dict[str, dict]:
        """{document_id: {"doc_sha", "doc_fingerprint", "chunks"}} по всей коллекции."""
        documents: dict[str, dict] = {}
        offset = None
        while True:
            points, offset = await self.client.scroll(
                self.collection, limit=_SCROLL_BATCH, offset=offset, with_vectors=False,
                with_payload=["document_id", "doc_sha", "doc_fingerprint"],
            )
            for point in points:
                info = documents.setdefault(point.payload["document_id"], {
                    "doc_sha": point.payload.get("doc_sha"), "doc_fingerprint": point.payload.get("doc_fingerprint"),
                    "chunks": 0,
                })
                info["chunks"] += 1
            if offset is None:
                return documents

    async def delete_documents(self, document_ids: list[str]) -> None:
        if document_ids:
            await self.client.delete(self.collection, points_selector=models.FilterSelector(
                filter=models.Filter(must=[_condition("document_id", document_ids)])))

    async def upsert(self, chunks: list[dict], vectors: list[list[float]]) -> None:
        points = [
            models.PointStruct(id=point_id(chunk["chunk_id"]), vector=vector, payload=chunk)
            for chunk, vector in zip(chunks, vectors, strict=True)
        ]
        await self.client.upsert(self.collection, points=points)

    async def search(self, vector: list[float], limit: int, filters: dict | None = None) -> list[dict]:
        query_filter = models.Filter(must=[_condition(k, v) for k, v in filters.items()]) if filters else None
        response = await self.client.query_points(
            self.collection, query=vector, limit=limit, query_filter=query_filter, with_payload=True,
        )
        return [{**point.payload, "score": point.score} for point in response.points]

    async def ping(self) -> None:
        await self.client.get_collections()


def point_id(chunk_id: str) -> str:
    """Детерминированный UUID: повторная индексация того же chunk перезаписывает точку."""
    return str(uuid.uuid5(uuid.NAMESPACE_URL, chunk_id))


def _condition(key: str, value) -> models.FieldCondition:
    if isinstance(value, (list, tuple, set)):
        return models.FieldCondition(key=key, match=models.MatchAny(any=list(value)))
    return models.FieldCondition(key=key, match=models.MatchValue(value=value))
