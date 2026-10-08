"""Инкрементальная индексация: векторизуются только документы, чьи chunks изменились.

Отпечаток документа — хеш текстов его chunks. Он меняется и при новой версии в источнике
(новый git blob SHA), и при изменении очистки или нормализации, когда SHA прежний.
Chunks изменённого документа удаляются и индексируются заново, пропавшие документы удаляются.
"""

import hashlib
import logging
from collections import defaultdict
from dataclasses import dataclass

from src.embeddings.embedder import Embedder
from src.retrieval.vector_store import QdrantStore

log = logging.getLogger(__name__)


@dataclass
class IndexStats:
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    chunks_indexed: int = 0


def document_fingerprint(chunks: list[dict]) -> str:
    return hashlib.sha1("\x1f".join(chunk["text"] for chunk in chunks).encode("utf-8")).hexdigest()


def index_chunks(chunks: list[dict], embedder: Embedder, store: QdrantStore, batch_size: int = 256) -> IndexStats:
    store.ensure_collection(embedder.dim)
    by_document: dict[str, list[dict]] = defaultdict(list)
    for chunk in chunks:
        by_document[chunk["document_id"]].append(chunk)
    fingerprints = {doc_id: document_fingerprint(doc_chunks) for doc_id, doc_chunks in by_document.items()}

    indexed = store.indexed_documents()
    changed = [doc_id for doc_id, fingerprint in fingerprints.items() if indexed.get(doc_id) != fingerprint]
    removed = [doc_id for doc_id in indexed if doc_id not in by_document]

    stats = IndexStats(
        added=sum(1 for doc_id in changed if doc_id not in indexed),
        unchanged=len(by_document) - len(changed),
        deleted=len(removed),
    )
    stats.updated = len(changed) - stats.added

    # Старые chunks изменённого документа удаляются до записи новых: число chunks могло измениться.
    store.delete_documents([doc_id for doc_id in changed if doc_id in indexed] + removed)

    pending = [
        {**chunk, "doc_fingerprint": fingerprints[doc_id]} for doc_id in changed for chunk in by_document[doc_id]
    ]
    for start in range(0, len(pending), batch_size):
        batch = pending[start:start + batch_size]
        store.upsert(batch, embedder.embed_documents([chunk["text"] for chunk in batch]))
        log.info("Проиндексировано %d/%d chunks", start + len(batch), len(pending))
    stats.chunks_indexed = len(pending)
    return stats
