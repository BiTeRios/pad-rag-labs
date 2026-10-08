"""Индексация: документы из ingestion-service → очистка и chunking → векторы inference-service → Qdrant.

Инкрементально (как в Lab1): отпечаток документа — хеш текстов его chunks. Совпал — документ не
векторизуется заново; изменился — старые chunks удаляются, новые записываются. Документ, удалённый
в источнике, удаляется из индекса. Задачи выполняются по одной (lock): событие и ручная сверка
не пишут в индекс одновременно.
"""

import asyncio
import hashlib
import logging
import re
import time
from collections.abc import Awaitable, Callable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime

from indexing_service.preprocessing.chunking import chunk_document
from indexing_service.preprocessing.cleaning import clean_markdown
from indexing_service.preprocessing.normalization import normalize_text
from indexing_service.store import VectorStore
from rag_common.errors import ServiceUnavailable
from rag_common.http import ServiceClient

log = logging.getLogger(__name__)


@dataclass
class JobStats:
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    empty: int = 0  # после очистки текста нет (страницы-заглушки)
    chunks_indexed: int = 0


def document_fingerprint(chunks: list[dict]) -> str:
    return hashlib.sha1("\x1f".join(chunk["text"] for chunk in chunks).encode("utf-8")).hexdigest()


def collection_name(prefix: str, model: str, strategy: str, size: int, overlap: int, include_heading: bool) -> str:
    model_slug = re.sub(r"[^a-z0-9]+", "-", model.split("/")[-1].lower()).strip("-")
    return f"{prefix}__{model_slug}__{strategy}-{size}-{overlap}-{'h' if include_heading else 'nh'}"


class Indexer:
    def __init__(self, store: VectorStore, ingestion: ServiceClient, inference: ServiceClient, settings):
        self.store = store
        self.ingestion = ingestion
        self.inference = inference
        self.settings = settings
        self.lock = asyncio.Lock()
        self.embedding_model: str | None = None
        self.current_job: dict | None = None
        self.last_job: dict | None = None

    async def prepare(self) -> None:
        """Коллекция зависит от модели эмбеддингов: модель и размерность берутся у inference-service."""
        if self.store.collection:
            return
        info = await self.inference.get("/internal/info")
        if not info["loaded"]:
            raise ServiceUnavailable("inference-service ещё загружает модели")
        s = self.settings
        name = collection_name(s.collection_prefix, info["embedding_model"], s.chunk_strategy, s.chunk_size,
                               s.chunk_overlap if s.chunk_strategy == "fixed" else 0, s.include_heading)
        await self.store.ensure_collection(name, info["dim"])
        self.embedding_model = info["embedding_model"]
        log.info("Коллекция %s готова", name)

    async def run_job(self, trigger: str, job: Callable[[], Awaitable[JobStats]]) -> JobStats:
        async with self.lock:
            started, started_at = time.perf_counter(), datetime.now(UTC).isoformat()
            self.current_job = {"trigger": trigger, "started_at": started_at}
            try:
                stats = await job()
            except Exception as error:
                self.last_job = {"trigger": trigger, "started_at": started_at, "status": "failed",
                                 "error": f"{type(error).__name__}: {error}"[:500]}
                raise
            finally:
                self.current_job = None
            duration = round(time.perf_counter() - started, 1)
            self.last_job = {"trigger": trigger, "started_at": started_at, "status": "succeeded",
                             "duration_s": duration, "stats": asdict(stats)}
            log.info("Индексация (%s) за %.1f с", trigger, duration, extra=asdict(stats))
            return stats

    async def apply(self, changed: list[str], deleted: list[str]) -> JobStats:
        await self.prepare()
        indexed = await self.store.indexed_documents()
        stats = JobStats()
        deleted = list(deleted)
        batch_size = self.settings.fetch_batch
        for start in range(0, len(changed), batch_size):
            batch = changed[start:start + batch_size]
            documents = await self.ingestion.post("/internal/documents/batch", json={"ids": batch})
            returned = {document["id"] for document in documents}
            deleted += [doc_id for doc_id in batch if doc_id not in returned]  # удалён после события
            for document in documents:
                await self._index_document(document, indexed.get(document["id"]), stats)
            log.info("Обработано документов %d/%d", min(start + batch_size, len(changed)), len(changed))

        to_delete = sorted({doc_id for doc_id in deleted if doc_id in indexed})
        await self.store.delete_documents(to_delete)
        stats.deleted = len(to_delete)
        return stats

    async def reconcile(self) -> JobStats:
        """Сверка индекса с корпусом: догоняет пропущенные события и первый запуск."""
        await self.prepare()
        source = {item["id"]: item["sha"] for item in await self.ingestion.get("/internal/documents")}
        indexed = await self.store.indexed_documents()
        changed = sorted(doc_id for doc_id, sha in source.items() if indexed.get(doc_id, {}).get("doc_sha") != sha)
        deleted = sorted(doc_id for doc_id in indexed if doc_id not in source)
        log.info("Сверка: к индексации %d, к удалению %d", len(changed), len(deleted))
        return await self.apply(changed, deleted)

    async def _index_document(self, document: dict, known: dict | None, stats: JobStats) -> None:
        chunks = self.build_chunks(document)
        if not chunks:
            stats.empty += 1
            if known:
                await self.store.delete_documents([document["id"]])
            return
        fingerprint = document_fingerprint(chunks)
        if known and known["doc_fingerprint"] == fingerprint:
            stats.unchanged += 1  # SHA изменился, а текст chunks — нет (например, правка front matter)
            return
        if known:
            await self.store.delete_documents([document["id"]])  # число chunks могло измениться
            stats.updated += 1
        else:
            stats.added += 1
        chunks = [{**chunk, "doc_fingerprint": fingerprint} for chunk in chunks]
        for start in range(0, len(chunks), self.settings.embed_batch):
            batch = chunks[start:start + self.settings.embed_batch]
            response = await self.inference.post(
                "/internal/embed", json={"texts": [chunk["text"] for chunk in batch], "kind": "passage"})
            await self.store.upsert(batch, response["vectors"])
        stats.chunks_indexed += len(chunks)

    def build_chunks(self, document: dict) -> list[dict]:
        text = normalize_text(clean_markdown(document["content"]))
        if not text:
            return []
        s = self.settings
        doc = {"document_id": document["id"], "text": text, "sha": document["sha"],
               **{field: document.get(field) for field in ("source", "url", "title", "section", "updated_at")}}
        return chunk_document(doc, s.chunk_strategy, s.chunk_size, s.chunk_overlap, s.include_heading)
