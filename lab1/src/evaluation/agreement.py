"""Согласие LLM-судьи с экспертной разметкой (experiments/manual_review.yaml).

Запуск: python -m src.evaluation.agreement --name baseline
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

from src.config import LAB_ROOT, load_config, resolve_path

REVIEW_FILE = LAB_ROOT / "experiments" / "manual_review.yaml"


def agreement(records: list[dict], review: dict[str, dict]) -> dict:
    """Для correctness и faithfulness: доля точных совпадений, в пределах ±1, средние (0..1) и куда отклоняется судья."""
    result = {}
    for metric in ("correctness", "faithfulness"):
        pairs = [
            (record[metric], review[record["id"]][metric])
            for record in records
            if record["id"] in review and record.get(metric) is not None
        ]
        if not pairs:
            continue
        result[metric] = {
            "n": len(pairs),
            "exact": round(sum(judge == expert for judge, expert in pairs) / len(pairs), 3),
            "within_1": round(sum(abs(judge - expert) <= 1 for judge, expert in pairs) / len(pairs), 3),
            "judge_mean": round(sum(judge for judge, _ in pairs) / len(pairs) / 2, 3),
            "expert_mean": round(sum(expert for _, expert in pairs) / len(pairs) / 2, 3),
            "judge_stricter": sum(judge < expert for judge, expert in pairs),
            "judge_lenient": sum(judge > expert for judge, expert in pairs),
            "disagreements": [record_id for record_id, (judge, expert) in _ids(records, review, metric) if judge != expert],
        }
    return result


def _ids(records, review, metric):
    for record in records:
        if record["id"] in review and record.get(metric) is not None:
            yield record["id"], (record[metric], review[record["id"]][metric])


def load_review(path: Path = REVIEW_FILE) -> dict[str, dict]:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Согласие LLM-судьи с экспертной разметкой")
    parser.add_argument("--name", default="baseline", help="имя прогона в experiments/results")
    args = parser.parse_args(argv)

    cfg = load_config()
    results = resolve_path(cfg["evaluation"]["results_dir"]) / args.name / "results.jsonl"
    records = [json.loads(line) for line in results.read_text(encoding="utf-8").splitlines()]
    report = agreement(records, load_review())
    print(json.dumps(report, ensure_ascii=False, indent=2))
    (results.parent / "agreement.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
