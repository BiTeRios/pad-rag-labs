"""Эксперименты L1-E1…E9 по сетке из configs/experiments.yaml.

Каждый вариант — прогон evaluate() с переопределёнными параметрами; недостающий индекс Qdrant
строится автоматически (инкрементально: готовые коллекции не пересчитываются).
Итог эксперимента — experiments/results/<id>/comparison.{md,json}.

Запуск: python -m src.evaluation.experiments [--only E1,E4] [--list]
"""

import argparse
import json
import logging
import re
import shutil
import sys
import time

import yaml

from src.config import load_config, resolve_path
from src.embeddings.embedder import release_gpu_memory
from src.embeddings.indexer import index_chunks
from src.evaluation.evaluate import evaluate
from src.factory import build_embedder, chunking_params, collection_name, llm_key, model_key, open_qdrant
from src.logging_setup import setup_logging
from src.preprocessing.pipeline import build_chunks, read_jsonl
from src.retrieval.vector_store import QdrantStore

log = logging.getLogger("experiments")

# (ключ, заголовок, направление: 1 — больше лучше, -1 — меньше лучше, 0 — без выделения)
RETRIEVAL_COLUMNS = [
    ("hit@1", "Hit@1", 1),
    ("hit@k", "Hit@{k}", 1),
    ("recall@k", "Recall@{k}", 1),
    ("precision@k", "Precision@{k}", 1),
    ("mrr", "MRR", 1),
    ("recall_multi_doc", "Recall@{k} multi-doc", 1),
    ("no_answer_empty", "Нет ответа → пустой контекст", 1),
    ("answerable_empty", "Есть ответ → пустой контекст", -1),
    ("latency_ms", "Поиск, мс", -1),
    ("chunks", "Chunks в индексе", 0),
]
GENERATION_COLUMNS = [
    ("correct_refusal", "Верные отказы", 1),
    ("false_refusal", "Ложные отказы", -1),
    ("citation_hit", "Citation hit", 1),
    ("correctness", "Correctness", 1),
    ("faithfulness", "Faithfulness", 1),
    ("claim_support", "Claim support", 1),
    ("generation_s", "Генерация, с", -1),
]
# Результаты вариантов в текущем процессе: одинаковый вариант в разных экспериментах (strict + qwen3:8b
# в E8 и E9) не прогоняется дважды — с генерацией и судьёй это минуты.
_DONE: dict[str, tuple[dict, str]] = {}

PER_K_COLUMNS = [("hit", "Hit@K", 1), ("recall", "Recall@K", 1), ("precision", "Precision@K", 1)]


def load_experiments(cfg: dict) -> dict:
    with resolve_path(cfg["evaluation"]["experiments_file"]).open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def variant_settings(cfg: dict, variant: dict) -> dict:
    """Параметры evaluate() для варианта: всё, что не задано, берётся из config (baseline).

    Значения по умолчанию подставляются явно, чтобы одинаковые варианты разных экспериментов совпадали.
    """
    chunking = {**chunking_params(cfg), **variant.get("chunking", {})}
    if chunking["strategy"] != "fixed":
        chunking["chunk_overlap"] = 0
    return {
        "model": model_key(cfg, variant.get("model")),
        "chunking": chunking,
        "use_reranker": variant.get("reranker", cfg["reranker"]["enabled"]),
        "llm": llm_key(cfg, variant.get("llm")),
        "prompt": variant.get("prompt") or cfg["generation"]["prompt"],
        "top_k": variant.get("top_k") or cfg["retrieval"]["top_k"],
        **variant.get("pipeline", {}),
    }


def ensure_indexes(cfg: dict, settings: list[dict]) -> dict[str, int]:
    """Строит недостающие коллекции; возвращает число chunks в каждой."""
    documents = read_jsonl(resolve_path(cfg["preprocessing"]["documents_file"]))
    counts: dict[str, int] = {}
    embedders: dict = {}
    for item in settings:
        name = collection_name(cfg, item["model"], item["chunking"])
        if name in counts:
            continue
        client = open_qdrant(cfg)
        try:
            store = QdrantStore(client, name)
            if item["model"] not in embedders:
                embedders[item["model"]] = build_embedder(cfg, item["model"])
            started = time.perf_counter()
            stats = index_chunks(
                build_chunks(documents, **item["chunking"]), embedders[item["model"]], store,
                cfg["vector_store"]["upsert_batch"],
            )
            counts[name] = store.count()
            if stats.chunks_indexed:
                print(f"  индекс {name}: {stats.chunks_indexed} chunks за {time.perf_counter() - started:.0f} с", flush=True)
        finally:
            client.close()
    embedders.clear()
    release_gpu_memory()
    return counts


def summary_row(variant: str, summary: dict, top_k: int, chunks: int | None) -> dict:
    retrieval = summary["retrieval"]
    overall = retrieval["overall"]
    row = {
        "variant": variant,
        "hit@1": overall["hit@1"],
        "hit@k": overall[f"hit@{top_k}"],
        "recall@k": overall[f"recall@{top_k}"],
        "precision@k": overall[f"precision@{top_k}"],
        "mrr": overall["mrr"],
        "recall_multi_doc": retrieval["by_type"].get("multi_doc", {}).get(f"recall@{top_k}"),
        "no_answer_empty": retrieval["no_answer_empty_context_rate"],
        "answerable_empty": retrieval.get("answerable_empty_context_rate"),
        "latency_ms": round(summary["latency_s"]["retrieval"] * 1000) if summary["latency_s"]["retrieval"] else None,
        "chunks": chunks,
    }
    if "generation" in summary:
        generation = summary["generation"]
        row.update(
            correct_refusal=generation["correct_refusal_rate"],
            false_refusal=generation["false_refusal_rate"],
            citation_hit=generation["citation_hit_rate"],
            generation_s=summary["latency_s"].get("generation"),
        )
    if "judge" in summary:
        answerable = summary["judge"]["answerable"]
        row.update(
            correctness=answerable["correctness"],
            faithfulness=answerable["faithfulness"],
            claim_support=answerable.get("claim_support"),
        )
    return row


def per_k_rows(summary: dict, k_values: list[int]) -> list[dict]:
    overall = summary["retrieval"]["overall"]
    return [
        {"variant": f"K={k}", **{name: overall[f"{name}@{k}"] for name, _, _ in PER_K_COLUMNS}} for k in k_values
    ]


def render_comparison(exp_id: str, spec: dict, rows: list[dict], top_k: int) -> str:
    columns = PER_K_COLUMNS if spec.get("per_k") else RETRIEVAL_COLUMNS + GENERATION_COLUMNS
    columns = [column for column in columns if any(row.get(column[0]) is not None for row in rows)]
    headers = [header.format(k=top_k) for _, header, _ in columns]
    lines = [
        f"# {exp_id}. {spec['title']}", "", f"Вопрос: {spec['question']}.", "",
        "| Вариант | " + " | ".join(headers) + " |",
        "|---|" + "--:|" * len(columns),
    ]
    best = {key: _best(rows, key, direction) for key, _, direction in columns}
    for row in rows:
        cells = []
        for key, _, _ in columns:
            text = _fmt(row.get(key))
            cells.append(f"**{text}**" if best[key] is not None and row.get(key) == best[key] else text)
        lines.append(f"| {row['variant']} | " + " | ".join(cells) + " |")
    lines += ["", "Жирным — лучшее значение в столбце. Подробности по вопросам — в папке варианта (report.md)."]
    return "\n".join(lines) + "\n"


def _best(rows: list[dict], key: str, direction: int):
    values = [row[key] for row in rows if row.get(key) is not None]
    if direction == 0 or len(set(values)) < 2:
        return None
    return max(values) if direction > 0 else min(values)


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _slug(name: str) -> str:
    return re.sub(r"[^\w.+-]+", "_", name).strip("_")


def run_experiment(cfg: dict, exp_id: str, spec: dict) -> list[dict]:
    variants = {name: variant_settings(cfg, variant or {}) for name, variant in spec["variants"].items()}
    counts = ensure_indexes(cfg, list(variants.values()))
    generate = spec.get("generate", False)
    rows = []
    for name, settings in variants.items():
        started = time.perf_counter()
        run_name = f"{exp_id}/{_slug(name)}"
        judge = spec.get("judge", generate)
        key = json.dumps({**settings, "generate": generate, "judge": judge}, sort_keys=True, ensure_ascii=False)
        if key in _DONE:
            result, source = _DONE[key]
            results_dir = resolve_path(cfg["evaluation"]["results_dir"])
            shutil.copytree(results_dir / source, results_dir / run_name, dirs_exist_ok=True)
            print(f"  {exp_id} {name}: тот же вариант, что {source} — результат переиспользован", flush=True)
        else:
            result = evaluate(cfg, run_name, generate=generate, judge=judge, **settings)
            _DONE[key] = (result, run_name)
        top_k = result["params"]["top_k"]
        chunks = counts[collection_name(cfg, settings["model"], settings["chunking"])]
        if spec.get("per_k"):
            rows += per_k_rows(result["summary"], cfg["evaluation"]["k_values"])
        else:
            rows.append(summary_row(name, result["summary"], top_k, chunks))
        overall = result["summary"]["retrieval"]["overall"]
        print(f"  {exp_id} {name}: Recall@{top_k} {overall[f'recall@{top_k}']}, MRR {overall['mrr']} "
              f"({time.perf_counter() - started:.0f} с)", flush=True)

    out_dir = resolve_path(cfg["evaluation"]["results_dir"]) / exp_id
    out_dir.mkdir(parents=True, exist_ok=True)
    top_k = cfg["retrieval"]["top_k"]
    (out_dir / "comparison.json").write_text(
        json.dumps({"id": exp_id, **{k: v for k, v in spec.items() if k != "variants"}, "rows": rows},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "comparison.md").write_text(render_comparison(exp_id, spec, rows, top_k), encoding="utf-8")
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Эксперименты по сетке configs/experiments.yaml")
    parser.add_argument("--only", help="id экспериментов через запятую (по умолчанию все без генерации)")
    parser.add_argument("--list", action="store_true", help="показать эксперименты и выйти")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--log-level", default="WARNING")
    args = parser.parse_args(argv)

    cfg = load_config(args.config)
    setup_logging(resolve_path(cfg["evaluation"]["log_file"]), args.log_level)
    experiments = load_experiments(cfg)
    if args.list:
        for exp_id, spec in experiments.items():
            kind = "генерация" if spec.get("generate") else "retrieval"
            print(f"{exp_id}: {spec['title']} ({kind}, вариантов {len(spec['variants'])})")
        return 0

    if args.only:
        selected = args.only.split(",")
        unknown = [exp_id for exp_id in selected if exp_id not in experiments]
        if unknown:
            log.error("Нет экспериментов %s в %s", unknown, cfg["evaluation"]["experiments_file"])
            return 1
    else:
        selected = [exp_id for exp_id, spec in experiments.items() if not spec.get("generate")]

    for exp_id in selected:
        started = time.perf_counter()
        print(f"{exp_id}. {experiments[exp_id]['title']}", flush=True)
        try:
            run_experiment(cfg, exp_id, experiments[exp_id])
        except (FileNotFoundError, ValueError) as error:
            log.error("%s: %s", exp_id, error)
            return 1
        print(f"  готово за {time.perf_counter() - started:.0f} с → "
              f"{resolve_path(cfg['evaluation']['results_dir']) / exp_id / 'comparison.md'}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
