"""CLI: python -m src.retrieval "вопрос" [--top-k N] [--no-rerank] [--section PATH] [--model KEY] [параметры chunking].

Показывает, сколько chunks осталось после каждого шага, и итоговые chunks со score.
"""

import argparse
import logging
import sys

from src.config import load_config, resolve_path
from src.factory import (
    add_chunking_args,
    build_embedder,
    build_pipeline,
    build_reranker,
    chunking_params,
    collection_name,
    model_key,
    open_qdrant,
)
from src.logging_setup import setup_logging
from src.retrieval.filters import body_text
from src.retrieval.retriever import Retriever
from src.retrieval.vector_store import QdrantStore

log = logging.getLogger("retrieval")

STAGE_NAMES = {
    "retrieved": "найдено",
    "score_threshold": "порог",
    "dedup": "без дублей",
    "min_length": "длина",
    "rerank": "reranker",
    "final": "итог",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Поиск контекста по вопросу")
    parser.add_argument("query", help="вопрос")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--top-k", type=int, help="переопределить retrieval.top_k")
    parser.add_argument("--no-rerank", action="store_true", help="без reranker")
    parser.add_argument("--section", help="искать только в разделе, например concepts/workloads/pods")
    parser.add_argument("--model", help="ключ модели из embeddings.models")
    add_chunking_args(parser)
    parser.add_argument("--log-level", default="WARNING")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(resolve_path(cfg["retrieval"]["log_file"]), args.log_level)

    model = model_key(cfg, args.model)
    collection = collection_name(cfg, model, chunking_params(cfg, args))
    client = open_qdrant(cfg)
    store = QdrantStore(client, collection)
    if not store.exists():
        log.error("Нет коллекции %s: сначала запустите python -m src.embeddings с теми же параметрами", collection)
        return 1

    use_reranker = cfg["reranker"]["enabled"] and not args.no_rerank
    pipeline = build_pipeline(
        cfg,
        Retriever(build_embedder(cfg, model), store),
        build_reranker(cfg) if use_reranker else None,
    )
    result = pipeline.run(args.query, args.top_k, {"section": args.section} if args.section else None)

    print(f"Коллекция: {collection}\nВопрос: {args.query}")
    print(" → ".join(f"{STAGE_NAMES[stage]} {count}" for stage, count in result.stages.items()) + "\n")
    if not result.chunks:
        print("Релевантного контекста не найдено.")
    for rank, chunk in enumerate(result.chunks, 1):
        scores = f"score {chunk['score']:.3f}"
        if "rerank_score" in chunk:
            scores += f", rerank {chunk['rerank_score']:.3f}"
        preview = " ".join(body_text(chunk).split())[:200]
        print(f"{rank}. [{scores}] {chunk['heading']}\n   {chunk['url']}\n   {preview}...\n")
    client.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
