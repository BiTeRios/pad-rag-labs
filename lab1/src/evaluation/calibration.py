"""Калибровка LLM-судьи: заведомо верные, частичные и неверные ответы на реальном контексте.

Проверяет, что судья различает ошибки, а не ставит высокие оценки всем подряд.
Запуск: python -m src.evaluation.calibration
"""

import json
import sys

from src.config import load_config, resolve_path
from src.embeddings.embedder import release_gpu_memory
from src.evaluation.dataset import load_eval_set
from src.factory import build_judge, build_retrieval
from src.generation.generator import format_context
from src.logging_setup import setup_logging

# (id вопроса, вид ответа, ответ, ожидаемая correctness, ожидаемая faithfulness)
CASES = [
    ("f04", "верный", "Порты NodePort по умолчанию выделяются из диапазона 30000–32767 [1].", 2, 2),
    ("f04", "неверный факт", "Порты NodePort по умолчанию выделяются из диапазона 20000–25000 [1].", 0, 0),
    ("f06", "неверный факт", "По умолчанию restartPolicy равен OnFailure [1].", 0, 0),
    ("f02", "не тот компонент", "Все данные кластера хранит kube-proxy в локальной базе SQLite на каждом узле [1].", 0, 0),
    ("f07", "выдуманная деталь", "Не более 1 MiB [1]. Лимит можно увеличить флагом --max-configmap-size у kube-apiserver [1].", 2, 1),
    ("s08", "неполный", "Параметр `maxUnavailable` [1].", 1, 2),
    ("m05", "только половина", "CronJob запускает Job'ы по расписанию [1].", 1, 2),
    ("c05", "обратный смысл", "Если readiness probe не проходит, kubelet перезапускает контейнер [1].", 0, 0),
    ("s03", "уклончивый", "Это зависит от настроек вашего кластера.", 0, 1),
]
METRICS = ("correctness", "faithfulness")


def main() -> int:
    cfg = load_config()
    setup_logging(resolve_path(cfg["evaluation"]["log_file"]), "WARNING")
    questions = {question.id: question for question in load_eval_set(resolve_path(cfg["evaluation"]["eval_set"]))}
    pipeline, client = build_retrieval(cfg)
    try:
        contexts = {
            qid: format_context(pipeline.run(questions[qid].question).chunks) for qid in {case[0] for case in CASES}
        }
    finally:
        client.close()
    del pipeline  # освобождаем видеопамять для судьи
    release_gpu_memory()

    judge = build_judge(cfg)
    rows = []
    print(f"{'id':4} {'вид ответа':18} {'ожид.':>6} {'судья':>6}  комментарий")
    for qid, kind, answer, want_c, want_f in CASES:
        question = questions[qid]
        verdict = judge.judge(question.question, question.expected_answer, contexts[qid], answer)
        rows.append({
            "id": qid, "kind": kind, "answer": answer, "expected": [want_c, want_f],
            "judge": [verdict.correctness, verdict.faithfulness], "comment": verdict.comment,
            "facts": verdict.facts, "unsupported_claims": verdict.unsupported_claims,
        })
        print(f"{qid:4} {kind:18} {want_c}/{want_f:<4} {verdict.correctness}/{verdict.faithfulness!s:<4}  {verdict.comment[:90]}")

    exact = {metric: sum(row["judge"][i] == row["expected"][i] for row in rows) for i, metric in enumerate(METRICS)}
    print(f"\nСовпало точно: correctness {exact['correctness']}/{len(rows)}, faithfulness {exact['faithfulness']}/{len(rows)}")
    out = resolve_path(cfg["evaluation"]["results_dir"]) / "calibration.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"exact": exact, "cases": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Сохранено: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
