from src.config import load_config
from src.evaluation.experiments import (
    load_experiments,
    per_k_rows,
    render_comparison,
    summary_row,
    variant_settings,
)

CFG = load_config()
VARIANT_KEYS = {"chunking", "model", "reranker", "pipeline", "llm", "prompt", "top_k"}
PIPELINE_KEYS = {"score_threshold", "rerank_min_score", "dedup_threshold", "min_chars", "max_per_document", "candidates"}


def summary(recall: float, empty: float = 0.0) -> dict:
    overall = {"mrr": 0.9, **{f"{m}@{k}": recall for k in (1, 5) for m in ("hit", "recall", "precision")}}
    return {
        "retrieval": {
            "overall": overall,
            "by_type": {"multi_doc": {"recall@5": recall / 2}},
            "no_answer_empty_context_rate": empty,
            "answerable_empty_context_rate": 0.0,
        },
        "latency_s": {"retrieval": 0.25},
    }


def test_experiments_file_is_valid():
    experiments = load_experiments(CFG)
    assert {f"E{n}" for n in range(1, 8)} <= set(experiments)
    for exp_id, spec in experiments.items():
        assert spec["title"] and spec["question"] and spec["variants"], exp_id
        for name, variant in spec["variants"].items():
            variant = variant or {}
            assert set(variant) <= VARIANT_KEYS, (exp_id, name)
            assert set(variant.get("pipeline", {})) <= PIPELINE_KEYS, (exp_id, name)
            variant_settings(CFG, variant)  # модели и стратегии существуют


def test_variant_settings_override_only_given_params():
    settings = variant_settings(CFG, {"chunking": {"strategy": "paragraph", "chunk_overlap": 200}, "reranker": False})
    assert settings["chunking"]["strategy"] == "paragraph"
    assert settings["chunking"]["chunk_overlap"] == 0  # overlap только у fixed
    assert settings["chunking"]["chunk_size"] == CFG["chunking"]["chunk_size"]
    assert settings["model"] == CFG["embeddings"]["model"] and settings["use_reranker"] is False

    thresholds = variant_settings(CFG, {"pipeline": {"score_threshold": 0.8}})
    assert thresholds["score_threshold"] == 0.8 and thresholds["use_reranker"] == CFG["reranker"]["enabled"]
    # умолчания подставлены явно: «strict» в E9 и «qwen3-8b» в E8 — один и тот же вариант
    assert variant_settings(CFG, {"prompt": CFG["generation"]["prompt"]}) == variant_settings(CFG, {"llm": CFG["llm"]["model"]})


def test_comparison_highlights_best_values():
    rows = [summary_row("a", summary(0.9), 5, 100), summary_row("b", summary(0.8, empty=0.5), 5, 200)]
    text = render_comparison("E0", {"title": "T", "question": "Q"}, rows, 5)
    assert "| a | **0.900** |" in text and "| b | 0.800 |" in text
    assert "**50%**" not in text and "**0.500**" in text  # доля пустого контекста на no_answer: больше лучше
    assert "Correctness" not in text  # без генерации столбцы LLM не выводятся


def test_per_k_rows():
    rows = per_k_rows(summary(0.7), [1, 5])
    assert [row["variant"] for row in rows] == ["K=1", "K=5"] and rows[1]["recall"] == 0.7
