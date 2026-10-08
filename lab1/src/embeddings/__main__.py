"""CLI: python -m src.embeddings [--model KEY] [--strategy S] [--chunk-size N] [--overlap N] [--no-heading] [--rebuild].

Строит или обновляет индекс Qdrant из data/processed/documents.jsonl. Повторный запуск
векторизует только новые и изменённые документы.
"""

import argparse
import logging
import sys
import time

from src.config import load_config, resolve_path
from src.embeddings.indexer import index_chunks
from src.factory import add_chunking_args, build_embedder, chunking_params, collection_name, model_key, open_qdrant
from src.logging_setup import setup_logging
from src.preprocessing.pipeline import build_chunks, read_jsonl
from src.retrieval.vector_store import QdrantStore

log = logging.getLogger("embeddings")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Векторизация chunks и обновление индекса Qdrant")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--model", help="ключ модели из embeddings.models")
    add_chunking_args(parser)
    parser.add_argument("--rebuild", action="store_true", help="очистить коллекцию и построить заново")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(resolve_path(cfg["embeddings"]["log_file"]), args.log_level)

    documents_path = resolve_path(cfg["preprocessing"]["documents_file"])
    if not documents_path.is_file():
        log.error("Нет %s: сначала запустите python -m src.preprocessing", documents_path)
        return 1

    model = model_key(cfg, args.model)
    chunking = chunking_params(cfg, args)
    chunks = build_chunks(read_jsonl(documents_path), **chunking)
    collection = collection_name(cfg, model, chunking)

    client = open_qdrant(cfg)
    store = QdrantStore(client, collection)
    if args.rebuild:
        store.clear()
        log.info("Коллекция %s очищена", collection)

    embedder = build_embedder(cfg, model)
    started = time.perf_counter()  # без загрузки модели: замер только индексации
    stats = index_chunks(chunks, embedder, store, cfg["vector_store"]["upsert_batch"])
    log.info(
        "Коллекция %s: документов добавлено %d, обновлено %d, без изменений %d, удалено %d; "
        "векторизовано chunks %d за %.1f с; всего точек %d",
        collection, stats.added, stats.updated, stats.unchanged, stats.deleted,
        stats.chunks_indexed, time.perf_counter() - started, store.count(),
    )
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
