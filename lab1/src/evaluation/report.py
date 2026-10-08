"""Сохранение результатов прогона: summary.json, results.jsonl и report.md для чтения."""

import json
from pathlib import Path

from src.evaluation.dataset import TYPE_NAMES, TYPES

SCORE = {0: "0 ✗", 1: "1 ~", 2: "2 ✓", None: "—"}


def save_run(out_dir: Path, name: str, params: dict, summary: dict, records: list[dict], k_values: list[int]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    public = [{key: value for key, value in record.items() if not key.startswith("_")} for record in records]
    (out_dir / "summary.json").write_text(
        json.dumps({"name": name, "params": params, "summary": summary}, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    with (out_dir / "results.jsonl").open("w", encoding="utf-8") as file:
        for record in public:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
    (out_dir / "report.md").write_text(render_report(name, params, summary, public, k_values), encoding="utf-8")


def load_run(out_dir: Path) -> tuple[dict, list[dict]]:
    """params и записи сохранённого прогона (для перезапуска судьи без retrieval и генерации)."""
    saved = json.loads((out_dir / "summary.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in (out_dir / "results.jsonl").read_text(encoding="utf-8").splitlines()]
    return saved["params"], records


def render_report(name: str, params: dict, summary: dict, records: list[dict], k_values: list[int]) -> str:
    top_k = params.get("top_k", 5)
    lines = [f"# Прогон `{name}`", "", "## Параметры", ""]
    lines += [f"- `{key}`: {value}" for key, value in params.items()]

    retrieval = summary["retrieval"]
    answerable = sum(1 for record in records if record["answerable"])
    lines += ["", f"## Retrieval ({answerable} вопросов с ответом)", "", "| K | Hit@K | Recall@K | Precision@K |", "|--:|--:|--:|--:|"]
    overall = retrieval["overall"]
    lines += [f"| {k} | {_f(overall[f'hit@{k}'])} | {_f(overall[f'recall@{k}'])} | {_f(overall[f'precision@{k}'])} |" for k in k_values]
    lines += ["", f"MRR: **{_f(overall['mrr'])}**", ""]
    lines += [f"| Тип | Hit@{top_k} | Recall@{top_k} | MRR |", "|---|--:|--:|--:|"]
    for kind, block in retrieval["by_type"].items():
        lines.append(f"| {TYPE_NAMES[kind]} | {_f(block.get(f'hit@{top_k}'))} | {_f(block.get(f'recall@{top_k}'))} | {_f(block['mrr'])} |")
    lines += [
        "",
        f"Вопросы без ответа: контекст отсечён фильтрами в {_pct(retrieval['no_answer_empty_context_rate'])} случаев.",
        f"Вопросы с ответом: контекст отсечён целиком в {_pct(retrieval.get('answerable_empty_context_rate'))} случаев.",
    ]

    if "generation" in summary:
        generation = summary["generation"]
        lines += [
            "", "## Генерация", "",
            f"- Отказ на вопросы без ответа (верно): **{_pct(generation['correct_refusal_rate'])}**",
            f"- Ложный отказ на вопросы с ответом: **{_pct(generation['false_refusal_rate'])}**",
            f"- Источники ответа содержат релевантный документ: **{_pct(generation['citation_hit_rate'])}**",
            f"- Вызовов LLM: {generation['llm_calls']} из {len(records)}",
        ]
    if "judge" in summary:
        judge = summary["judge"]
        lines += [
            "", "## Оценка судьи (0..1)", "",
            "| Группа | Correctness | Faithfulness | Claim support | N |", "|---|--:|--:|--:|--:|",
            _judge_row("все вопросы", judge["overall"]),
            _judge_row("с ответом", judge["answerable"]),
        ]
        lines += [_judge_row(TYPE_NAMES[kind], judge["by_type"][kind]) for kind in TYPES]
        lines += [
            "", "Correctness для вопросов без ответа: 1 — система отказалась. Faithfulness считается только для ответов, а не отказов.",
            "Claim support — доля утверждений ответа, для которых судья нашёл цитату в контексте (как faithfulness в RAGAS).",
        ]
        if judge["judge_failures"]:
            lines.append(f"Судья не смог оценить {judge['judge_failures']} ответ(ов).")
    if "latency_s" in summary:
        latency = summary["latency_s"]
        lines += ["", "Средняя задержка: " + ", ".join(f"{stage} {value} с" for stage, value in latency.items() if value is not None)]

    lines += ["", "## По вопросам", "", f"| id | Тип | Hit@{top_k} | RR | Отказ | Correctness | Faithfulness |", "|---|---|--:|--:|:-:|:-:|:-:|"]
    for record in records:
        metrics = record.get("metrics", {})
        refused = {True: "да", False: "нет"}.get(record.get("refused"), "—")
        lines.append(
            f"| {record['id']} | {TYPE_NAMES[record['type']]} | {_f(metrics.get(f'hit@{top_k}'))} | {_f(metrics.get('rr'))} "
            f"| {refused} | {SCORE[record.get('correctness')]} | {SCORE[record.get('faithfulness')]} |"
        )

    lines += ["", "## Подробно"]
    for record in records:
        lines += ["", f"### {record['id']} — {TYPE_NAMES[record['type']]}", "", f"**Вопрос:** {record['question']}", "",
                  f"**Эталон:** {record['expected_answer']}", ""]
        relevant = set(record["relevant_docs"])
        if relevant:
            lines.append(f"**Релевантные документы ({record['match']}):** " + ", ".join(f"`{doc}`" for doc in record["relevant_docs"]))
            lines.append("")
        lines.append(f"**Найдено (top-{top_k} из {len(record['retrieved'])}):** " + " → ".join(f"{k} {v}" for k, v in record["stages"].items()))
        for item in record["retrieved"][:top_k]:
            mark = "✓" if item["document_id"] in relevant else " "
            rerank = f", rerank {item['rerank_score']:.3f}" if item["rerank_score"] is not None else ""
            lines.append(f"{item['rank']}. {mark} `{item['document_id']}` — {item['heading']} (score {item['score']:.3f}{rerank})")
        if "answer" in record:
            lines += ["", "**Ответ:**", "", "> " + record["answer"].replace("\n", "\n> ")]
            if record["sources"]:
                lines += ["", "**Источники:** " + ", ".join(f"[{s['n']}] {s['url']}" for s in record["sources"])]
        if "correctness" in record:
            lines += ["", f"**Оценка:** correctness {SCORE[record['correctness']]}, faithfulness {SCORE[record['faithfulness']]}. {record['judge_comment']}"]
    return "\n".join(lines) + "\n"


def _judge_row(name: str, block: dict) -> str:
    return f"| {name} | {_f(block['correctness'])} | {_f(block['faithfulness'])} | {_f(block.get('claim_support'))} | {block['n']} |"

def _f(value) -> str:
    return "—" if value is None else f"{value:.3f}"


def _pct(value) -> str:
    return "—" if value is None else f"{value * 100:.0f}%"
