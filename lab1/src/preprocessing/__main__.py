"""CLI: python -m src.preprocessing [--strategy S] [--chunk-size N] [--overlap N] [--no-heading].

Без аргументов берёт параметры chunking из configs/config.yaml.
"""

import argparse
import logging
import statistics
import sys

from src.config import load_config, resolve_path
from src.factory import add_chunking_args, chunking_params
from src.logging_setup import setup_logging
from src.preprocessing.pipeline import build_chunks, load_documents, write_jsonl

log = logging.getLogger("preprocessing")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Очистка, нормализация и chunking документов")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    add_chunking_args(parser)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    paths = cfg["preprocessing"]
    setup_logging(resolve_path(paths["log_file"]), args.log_level)

    manifest_path = resolve_path(cfg["grabber"]["manifest_file"])
    if not manifest_path.is_file():
        log.error("Нет %s: сначала запустите python -m src.grabber", manifest_path)
        return 1

    params = chunking_params(cfg, args)
    documents = load_documents(resolve_path(cfg["grabber"]["raw_dir"]), manifest_path)
    chunks = build_chunks(documents, **params)
    write_jsonl(resolve_path(paths["documents_file"]), documents)
    write_jsonl(resolve_path(paths["chunks_file"]), chunks)

    empty = sum(1 for document in documents if not document["text"])
    lengths = [len(chunk["text"]) for chunk in chunks] or [0]
    log.info("Документов %d (пустых после очистки %d); параметры %s", len(documents), empty, params)
    log.info(
        "Chunks %d: длина средняя %d, медиана %d, мин %d, макс %d символов",
        len(chunks), statistics.mean(lengths), statistics.median(lengths), min(lengths), max(lengths),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
