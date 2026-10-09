"""Один прогон оценки с заданными параметрами: используется CLI и экспериментами."""

import logging
import time

from src.config import resolve_path
from src.embeddings.embedder import release_gpu_memory
from src.evaluation.dataset import load_eval_set
from src.evaluation.langfuse_run import RunTracing
from src.evaluation.report import load_run, save_run
from src.evaluation.runner import run_generation, run_judge, run_retrieval, summarize
from src.factory import (
    build_generator,
    build_judge,
    build_llm,
    build_retrieval,
    chunking_params,
    collection_name,
    llm_key,
    model_key,
)
from src.tracing import build_tracer

log = logging.getLogger(__name__)


def evaluate(
    cfg: dict,
    name: str,
    *,
    model: str | None = None,
    chunking: dict | None = None,
    use_reranker: bool | None = None,
    llm: str | None = None,
    prompt: str | None = None,
    top_k: int | None = None,
    generate: bool = True,
    judge: bool = True,
    question_ids: list[str] | None = None,
    **pipeline_overrides,
) -> dict:
    """Retrieval (+ генерация, + судья) по набору вопросов; результаты в <results_dir>/<name>/.

    Возвращает {"params", "summary", "records"}.
    """
    settings = cfg["evaluation"]
    k_values = settings["k_values"]
    top_k = top_k or cfg["retrieval"]["top_k"]
    model = model_key(cfg, model)
    chunking = chunking or chunking_params(cfg)
    questions = load_eval_set(resolve_path(settings["eval_set"]))
    if question_ids:
        questions = [question for question in questions if question.id in question_ids]

    started = time.perf_counter()
    tracer = build_tracer(cfg)
    pipeline, client = build_retrieval(
        cfg, model=model, chunking=chunking, use_reranker=use_reranker, tracer=tracer, **pipeline_overrides
    )
    tracing = RunTracing(tracer, name, settings["langfuse_dataset"],
                         tags=["evaluation", model, "rerank" if pipeline.reranker else "no-rerank"])
    tracing.sync_dataset(questions)
    try:
        records = run_retrieval(pipeline, questions, k_values, tracing)
    finally:
        client.close()

    params = {
        "collection": collection_name(cfg, model, chunking),
        "embedding_model": model,
        **{f"chunking.{key}": value for key, value in chunking.items()},
        "reranker": pipeline.reranker is not None,
        "candidates": pipeline.candidates,
        "score_threshold": pipeline.score_threshold,
        "dedup_threshold": pipeline.dedup_threshold,
        "min_chars": pipeline.min_chars,
        "rerank_min_score": pipeline.rerank_min_score if pipeline.reranker else None,
        "max_per_document": pipeline.max_per_document,
        "top_k": top_k,
        "questions": len(questions),
    }
    del pipeline  # эмбеддер и reranker больше не нужны: освобождаем видеопамять для LLM
    release_gpu_memory()

    if generate:
        llm = llm_key(cfg, llm)
        prompt = prompt or cfg["generation"]["prompt"]
        params.update(llm=llm, prompt=prompt)
        tracing.tags += [llm, f"prompt-{prompt}"]
        run_generation(build_generator(cfg, build_llm(cfg, llm, tracer), prompt), records, top_k, tracing)
        if judge:
            params["judge"] = settings["judge_llm"]
            run_judge(build_judge(cfg, tracer), records, tracing)

    summary = summarize(records, k_values, top_k)
    summary["elapsed_s"] = round(time.perf_counter() - started, 1)
    save_run(resolve_path(settings["results_dir"]) / name, name, params, summary, records, k_values)
    tracing.report(records, summary, top_k)
    log.info("Прогон %s: %d вопросов за %.0f с", name, len(records), summary["elapsed_s"])
    return {"params": params, "summary": summary, "records": records}


def rejudge(cfg: dict, source: str, name: str | None = None) -> dict:
    """Перезапуск только LLM-судьи на сохранённых ответах прогона source (без retrieval и генерации).

    Нужен при настройке промптов судьи: ответы и контекст берутся из results.jsonl.
    """
    settings = cfg["evaluation"]
    results_dir = resolve_path(settings["results_dir"])
    params, records = load_run(results_dir / source)
    if not records or "answer" not in records[0]:
        raise ValueError(f"в прогоне {source} нет ответов LLM: перезапуск судьи невозможен")
    if any("context_text" not in record for record in records):
        raise ValueError(f"в прогоне {source} не сохранён контекст: нужен новый полный прогон")

    started = time.perf_counter()
    params["judge"] = settings["judge_llm"]
    name = name or source
    tracer = build_tracer(cfg)
    tracing = RunTracing(tracer, name, tags=["evaluation", "rejudge"])  # без dataset run: вопросы не перезапускались
    run_judge(build_judge(cfg, tracer), records, tracing)
    summary = summarize(records, settings["k_values"], params["top_k"])
    summary["elapsed_s"] = round(time.perf_counter() - started, 1)
    save_run(results_dir / name, name, params, summary, records, settings["k_values"])
    tracing.report(records, summary, params["top_k"])
    log.info("Судья перезапущен на %s: %d вопросов за %.0f с", source, len(records), summary["elapsed_s"])
    return {"params": params, "summary": summary, "records": records}
