"""Сборка компонентов пайплайна из config: общие для CLI и экспериментов."""

import argparse

from src.config import resolve_path
from src.preprocessing.chunking import STRATEGIES


def add_chunking_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--strategy", choices=STRATEGIES, help="переопределить chunking.strategy")
    parser.add_argument("--chunk-size", type=int, help="переопределить chunking.chunk_size")
    parser.add_argument("--overlap", type=int, help="переопределить chunking.chunk_overlap")
    parser.add_argument("--no-heading", action="store_true", help="не добавлять путь заголовков в chunk")


def chunking_params(cfg: dict, args: argparse.Namespace | None = None) -> dict:
    """Параметры chunking из config с переопределениями из аргументов CLI."""
    chunking = cfg["chunking"]
    params = {key: chunking[key] for key in ("strategy", "chunk_size", "chunk_overlap", "include_heading")}
    if args is not None:
        params["strategy"] = args.strategy or params["strategy"]
        params["chunk_size"] = args.chunk_size or params["chunk_size"]
        params["chunk_overlap"] = params["chunk_overlap"] if args.overlap is None else args.overlap
        params["include_heading"] = params["include_heading"] and not args.no_heading
    if params["strategy"] != "fixed":
        params["chunk_overlap"] = 0  # overlap есть только у fixed; так одинаковые индексы не дублируются
    return params


def model_key(cfg: dict, override: str | None = None) -> str:
    key = override or cfg["embeddings"]["model"]
    if key not in cfg["embeddings"]["models"]:
        raise ValueError(f"модели '{key}' нет в embeddings.models: {list(cfg['embeddings']['models'])}")
    return key


def collection_name(cfg: dict, model: str, chunking: dict) -> str:
    """Одна коллекция на модель и параметры chunking, например k8s__multilingual-e5-base__heading-1000-0-h."""
    suffix = "h" if chunking["include_heading"] else "nh"
    params = f"{chunking['strategy']}-{chunking['chunk_size']}-{chunking['chunk_overlap']}-{suffix}"
    return f"{cfg['vector_store']['collection_prefix']}__{model}__{params}"


def build_embedder(cfg: dict, model: str):
    from src.embeddings.embedder import Embedder

    settings = cfg["embeddings"]
    spec = settings["models"][model]
    return Embedder(
        spec["name"],
        query_prefix=spec.get("query_prefix", ""),
        passage_prefix=spec.get("passage_prefix", ""),
        max_seq_length=spec.get("max_seq_length"),
        batch_size=settings["batch_size"],
        device=settings["device"],
    )


def build_reranker(cfg: dict):
    from src.reranking.reranker import Reranker

    settings = cfg["reranker"]
    return Reranker(
        settings["model"],
        max_length=settings["max_length"],
        batch_size=settings["batch_size"],
        device=settings["device"],
    )


def build_pipeline(cfg: dict, retriever, reranker=None, **overrides):
    """RetrievalPipeline с порогами из config; overrides — для CLI и экспериментов."""
    from src.retrieval.pipeline import RetrievalPipeline

    settings = cfg["filters"]
    params = {
        "top_k": cfg["retrieval"]["top_k"],
        "candidates": cfg["retrieval"]["candidates"],
        "score_threshold": settings["score_threshold"],
        "dedup_threshold": settings["dedup_threshold"],
        "min_chars": settings["min_chars"],
        "max_per_document": settings["max_per_document"],
        "metadata": settings["metadata"],
        "rerank_min_score": cfg["reranker"]["min_score"],
        **overrides,
    }
    return RetrievalPipeline(retriever, reranker, **params)


def llm_key(cfg: dict, override: str | None = None) -> str:
    key = override or cfg["llm"]["model"]
    if key not in cfg["llm"]["models"]:
        raise ValueError(f"LLM '{key}' нет в llm.models: {list(cfg['llm']['models'])}")
    return key


def build_llm(cfg: dict, key: str):
    from src.generation.llm import OllamaClient

    spec = cfg["llm"]["models"][key]
    return OllamaClient(
        cfg["llm"]["base_url"],
        spec["name"],
        temperature=spec.get("temperature", 0.1),
        num_ctx=spec.get("num_ctx", 8192),
        think=spec.get("think"),
        seed=spec.get("seed"),
        timeout_s=cfg["llm"]["timeout_s"],
    )


def load_prompt(cfg: dict, name: str | None = None) -> dict:
    import yaml

    settings = cfg["generation"]
    name = name or settings["prompt"]
    with resolve_path(settings["prompts_file"]).open(encoding="utf-8") as file:
        prompts = yaml.safe_load(file)
    if name not in prompts:
        raise ValueError(f"промпта '{name}' нет в {settings['prompts_file']}: {list(prompts)}")
    return prompts[name]


def build_generator(cfg: dict, llm, prompt_name: str | None = None):
    from src.generation.generator import AnswerGenerator

    settings = cfg["generation"]
    prompt = load_prompt(cfg, prompt_name)
    return AnswerGenerator(
        llm,
        system_prompt=prompt["system"].format(no_context_answer=settings["no_context_answer"]),
        user_template=prompt["user"],
        no_context_answer=settings["no_context_answer"],
        refusal_marker=settings["refusal_marker"],
    )


def build_rag(
    cfg: dict,
    *,
    model: str | None = None,
    chunking: dict | None = None,
    llm: str | None = None,
    prompt: str | None = None,
    use_reranker: bool | None = None,
    **pipeline_overrides,
):
    """RAG из config с переопределениями. Возвращает (rag, qdrant_client): клиент нужно закрыть."""
    from src.rag import RAG

    retrieval, client = build_retrieval(
        cfg, model=model, chunking=chunking, use_reranker=use_reranker, **pipeline_overrides
    )
    generator = build_generator(cfg, build_llm(cfg, llm_key(cfg, llm)), prompt)
    return RAG(retrieval, generator), client


def build_retrieval(
    cfg: dict,
    *,
    model: str | None = None,
    chunking: dict | None = None,
    use_reranker: bool | None = None,
    **pipeline_overrides,
):
    """RetrievalPipeline для коллекции модели и параметров chunking. Возвращает (pipeline, qdrant_client)."""
    from src.retrieval.retriever import Retriever
    from src.retrieval.vector_store import QdrantStore

    model = model_key(cfg, model)
    chunking = chunking or chunking_params(cfg)
    client = open_qdrant(cfg)
    store = QdrantStore(client, collection_name(cfg, model, chunking))
    if not store.exists():
        client.close()
        raise FileNotFoundError(f"нет коллекции {store.collection}: запустите python -m src.embeddings с теми же параметрами")

    if use_reranker is None:
        use_reranker = cfg["reranker"]["enabled"]
    pipeline = build_pipeline(
        cfg,
        Retriever(build_embedder(cfg, model), store),
        build_reranker(cfg) if use_reranker else None,
        **pipeline_overrides,
    )
    return pipeline, client


def build_judge(cfg: dict):
    from src.evaluation.judge import LLMJudge

    settings = cfg["evaluation"]
    prompts = {kind: load_prompt(cfg, name) for kind, name in settings["judge_prompts"].items()}
    return LLMJudge(build_llm(cfg, llm_key(cfg, settings["judge_llm"])), prompts)


def open_qdrant(cfg: dict):
    from qdrant_client import QdrantClient

    path = resolve_path(cfg["vector_store"]["path"])
    path.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(path))
