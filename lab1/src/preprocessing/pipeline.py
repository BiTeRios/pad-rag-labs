"""Пайплайн preprocessing: raw-документы + manifest → очищенные документы → chunks.

Функции переиспользуются экспериментами: chunking с разными параметрами строится
из одних и тех же очищенных документов.
"""

import json
import logging
from pathlib import Path
from typing import Iterable

from src.preprocessing.chunking import chunk_document
from src.preprocessing.cleaning import clean_markdown
from src.preprocessing.normalization import normalize_text

DOC_FIELDS = ("document_id", "source", "url", "title", "section", "updated_at", "sha")

log = logging.getLogger(__name__)


def load_documents(raw_dir: Path, manifest_path: Path) -> list[dict]:
    """Очищенные и нормализованные документы с metadata из manifest grabber'а."""
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    documents = []
    for document_id, meta in sorted(manifest["documents"].items()):
        raw_path = raw_dir / document_id
        if not raw_path.is_file():
            log.warning("Нет файла %s (manifest и data/raw расходятся, запустите grabber)", document_id)
            continue
        text = normalize_text(clean_markdown(raw_path.read_text(encoding="utf-8")))
        documents.append({**{field: meta.get(field) for field in DOC_FIELDS}, "text": text})
    return documents


def build_chunks(
    documents: list[dict],
    strategy: str,
    chunk_size: int,
    chunk_overlap: int = 0,
    include_heading: bool = True,
) -> list[dict]:
    return [
        chunk
        for document in documents
        if document["text"]
        for chunk in chunk_document(document, strategy, chunk_size, chunk_overlap, include_heading)
    ]


def write_jsonl(path: Path, rows: Iterable[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as file:
        return [json.loads(line) for line in file if line.strip()]
