import json

import pytest

from src.evaluation.dataset import EvalQuestion
from src.evaluation.judge import CORRECTNESS_SCHEMA, FAITHFULNESS_SCHEMA, LLMJudge, correctness_from_facts
from src.evaluation.metrics import hit_at, precision_at, recall_at, reciprocal_rank, retrieval_metrics
from src.evaluation.report import render_report, save_run
from src.evaluation.runner import run_generation, run_judge, run_retrieval, summarize
from src.generation.generator import AnswerGenerator
from src.generation.llm import LLMResponse
from src.retrieval.pipeline import RetrievalPipeline
from tests.helpers import make_chunk

RANKED = ["a", "x", "b", "a", "y"]


def test_hit_recall_precision_rr():
    assert hit_at(RANKED, {"b"}, 2) == 0 and hit_at(RANKED, {"b"}, 3) == 1
    assert recall_at(RANKED, {"a", "b"}, 1, "all") == 0.5
    assert recall_at(RANKED, {"a", "b"}, 3, "all") == 1.0
    assert recall_at(RANKED, {"a", "b"}, 1, "any") == 1.0
    assert precision_at(RANKED, {"a", "b"}, 4) == 0.75
    assert precision_at(["a"], {"a"}, 5) == 1.0  # фильтры вернули меньше K: делим на число возвращённых
    assert precision_at([], {"a"}, 5) == 0.0
    assert reciprocal_rank(RANKED, {"b"}) == pytest.approx(1 / 3)
    assert reciprocal_rank(RANKED, {"z"}) == 0.0


def test_retrieval_metrics_for_all_k():
    metrics = retrieval_metrics(RANKED, {"b"}, "any", [1, 3])
    assert metrics == {"rr": pytest.approx(1 / 3), "hit@1": 0.0, "recall@1": 0.0, "precision@1": 0.0,
                       "hit@3": 1.0, "recall@3": 1.0, "precision@3": pytest.approx(1 / 3)}


class StubRetriever:
    def __init__(self, by_query: dict[str, list[dict]]):
        self.by_query = by_query

    def retrieve(self, query, top_k=None, filters=None):
        return self.by_query.get(query, [])[:top_k]


class ScriptedLLM:
    """Отвечает по первому совпавшему ключу в сообщении пользователя."""

    def __init__(self, replies: dict[str, str], default: str = ""):
        self.replies = replies
        self.default = default
        self.calls: list[dict] = []

    def chat(self, system, user, schema=None):
        self.calls.append({"user": user, "schema": schema})
        text = next((reply for key, reply in self.replies.items() if key in user), self.default)
        return LLMResponse(text, "fake")


QUESTIONS = [
    EvalQuestion("f01", "factual", "Что такое Pod?", "Наименьшая единица.", ("pods",)),
    EvalQuestion("m01", "multi_doc", "Deployment vs StatefulSet?", "Разница.", ("deploy", "sts"), match="all"),
    EvalQuestion("n01", "no_answer", "Как приготовить борщ?", "Отказ.", ()),
    EvalQuestion("n02", "no_answer", "Сколько стоит GKE?", "Отказ.", ()),
]

CHUNKS = {
    "Что такое Pod?": [make_chunk("other", 0, "noise", score=0.9), make_chunk("pods", 0, "pod is smallest", score=0.8)],
    "Deployment vs StatefulSet?": [make_chunk("deploy", 0, "deployment", score=0.9), make_chunk("x", 0, "x", score=0.85)],
    "Сколько стоит GKE?": [make_chunk("quotas", 0, "resource quotas", score=0.8)],
}

REFUSAL = "В документации недостаточно информации для ответа на этот вопрос."
PROMPTS = {
    "correctness": {"system": "S", "user": "{question}|{expected}|{answer}"},
    "faithfulness": {"system": "S", "user": "{question}|{context}|{answer}"},
}


@pytest.fixture
def records():
    pipeline = RetrievalPipeline(StubRetriever(CHUNKS), top_k=5, candidates=20)
    records = run_retrieval(pipeline, QUESTIONS, [1, 2])
    llm = ScriptedLLM({"Что такое Pod?": "Pod — единица [2].", "Сколько стоит GKE?": "Около 70 долларов [1]."}, REFUSAL)
    run_generation(AnswerGenerator(llm, "S", "{context}\n{question}", REFUSAL, "недостаточно информации"), records, top_k=2)
    return records


def test_run_retrieval_computes_metrics_only_for_answerable(records):
    f01, m01, n01, n02 = records
    assert f01["metrics"]["hit@1"] == 0 and f01["metrics"]["hit@2"] == 1 and f01["metrics"]["rr"] == 0.5
    assert m01["metrics"]["recall@2"] == 0.5  # найден deploy, но не sts
    assert "metrics" not in n01 and n01["empty_context"] and not n02["empty_context"]
    assert [item["document_id"] for item in f01["retrieved"]] == ["other", "pods"]


def test_run_generation_records_answers_refusals_and_citations(records):
    f01, m01, n01, n02 = records
    assert f01["refused"] is False and f01["citation_hit"] == 1.0
    assert m01["refused"] is True and m01["citation_hit"] is None  # LLM ответила фразой отказа
    assert n01["refused"] and not n01["llm_called"]  # пустой контекст: LLM не вызывалась
    assert n02["refused"] is False and n02["sources"][0]["document_id"] == "quotas"


def test_run_judge_scores_and_skips_refusals(records):
    judge_llm = ScriptedLLM({}, json.dumps({"correctness": 2, "faithfulness": 1, "comment": "ok"}))
    run_judge(LLMJudge(judge_llm, PROMPTS), records)
    f01, m01, n01, n02 = records

    assert (f01["correctness"], f01["faithfulness"]) == (2, 1)
    assert (m01["correctness"], m01["faithfulness"]) == (0, None)  # ложный отказ
    assert (n01["correctness"], n01["faithfulness"]) == (2, None)  # верный отказ
    assert (n02["correctness"], n02["faithfulness"]) == (0, 1)  # ответил на вопрос без ответа
    assert len(judge_llm.calls) == 4  # два ответа × (correctness + faithfulness)
    assert [c["schema"] for c in judge_llm.calls[:2]] == [CORRECTNESS_SCHEMA, FAITHFULNESS_SCHEMA]
    assert "|" + REFUSAL not in judge_llm.calls[0]["user"]  # в correctness нет контекста
    assert judge_llm.calls[0]["user"].count("|") == 2 and judge_llm.calls[1]["user"].count("|") >= 2


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        (["есть", "есть"], 2),
        (["есть", "нет"], 1),
        (["частично"], 1),
        (["есть", "противоречит"], 0),  # противоречие перевешивает верные факты
        (["нет", "нет"], 0),
        ([], 1),  # фактов нет — берётся оценка модели
    ],
)
def test_correctness_is_derived_from_facts(statuses, expected):
    assert correctness_from_facts([{"fact": "f", "status": s} for s in statuses], fallback=1) == expected


def test_judge_derives_correctness_from_facts_and_keeps_claims():
    reply = json.dumps({
        "facts": [{"fact": "Always", "status": "противоречит"}],
        "claims": [
            {"claim": "лимит 1 MiB", "fragment": 1, "status": "подтверждено"},
            {"claim": "флаг --max-configmap-size", "fragment": 0, "status": "не подтверждено"},
        ],
        "correctness": 1, "faithfulness": 1, "comment": "c",
    })
    verdict = LLMJudge(ScriptedLLM({}, reply), PROMPTS).judge("q", "e", "c", "a")
    assert (verdict.correctness, verdict.faithfulness) == (0, 1)  # faithfulness — оценка модели
    assert verdict.unsupported_claims == ["флаг --max-configmap-size"] and verdict.claim_support == 0.5


def test_judge_gives_full_faithfulness_when_every_claim_has_evidence():
    reply = json.dumps({
        "claims": [{"claim": "лимит 1 MiB", "fragment": 1, "status": "подтверждено"}],
        "faithfulness": 1, "comment": "c",
    })
    verdict = LLMJudge(ScriptedLLM({}, reply), PROMPTS).faithfulness("q", "c", "a")
    assert (verdict.faithfulness, verdict.claim_support, verdict.unsupported_claims) == (2, 1.0, [])


def test_judge_handles_invalid_json():
    verdict = LLMJudge(ScriptedLLM({}, "не JSON"), PROMPTS).judge("q", "e", "c", "a")
    assert verdict.correctness is None and "некорректный" in verdict.comment


def test_summary_and_report(records, tmp_path):
    judge_llm = ScriptedLLM({}, json.dumps({"correctness": 2, "faithfulness": 2, "comment": "ok"}))
    run_judge(LLMJudge(judge_llm, PROMPTS), records)

    summary = summarize(records, [1, 2], top_k=2)

    retrieval = summary["retrieval"]
    assert retrieval["overall"]["hit@2"] == 1.0 and retrieval["overall"]["mrr"] == 0.75
    assert retrieval["by_type"]["multi_doc"]["recall@2"] == 0.5
    assert retrieval["no_answer_empty_context_rate"] == 0.5
    generation = summary["generation"]
    assert (generation["correct_refusal_rate"], generation["false_refusal_rate"]) == (0.5, 0.5)
    assert generation["citation_hit_rate"] == 1.0 and generation["llm_calls"] == 3
    assert summary["judge"]["answerable"]["correctness"] == 0.5  # f01 верно (2), m01 ложный отказ (0)
    assert summary["judge"]["no_answer"]["correctness"] == 0.5  # n01 отказ (2), n02 ответил (0)

    save_run(tmp_path / "run", "test", {"top_k": 2}, summary, records, [1, 2])
    report = (tmp_path / "run" / "report.md").read_text(encoding="utf-8")
    assert "### f01" in report and "**Эталон:**" in report and "**Ответ:**" in report
    assert len((tmp_path / "run" / "results.jsonl").read_text(encoding="utf-8").splitlines()) == 4
    assert "_chunks" not in (tmp_path / "run" / "results.jsonl").read_text(encoding="utf-8")


def test_saved_run_can_be_rejudged_without_generation(records, tmp_path):
    from src.evaluation.report import load_run

    save_run(tmp_path / "run", "test", {"top_k": 2}, summarize(records, [1, 2], 2), records, [1, 2])
    params, loaded = load_run(tmp_path / "run")
    judge_llm = ScriptedLLM({}, json.dumps({"correctness": 2, "faithfulness": 2, "comment": "ok"}))

    run_judge(LLMJudge(judge_llm, PROMPTS), loaded)

    assert params == {"top_k": 2} and loaded[0]["context_text"].startswith("[1]")
    assert "pod is smallest" in judge_llm.calls[1]["user"]  # faithfulness получил сохранённый контекст
    assert summarize(loaded, [1, 2], 2)["judge"]["answerable"]["n"] == 2


def test_agreement_with_expert_review():
    from src.evaluation.agreement import agreement

    records = [
        {"id": "a", "correctness": 2, "faithfulness": 1},
        {"id": "b", "correctness": 0, "faithfulness": 2},
        {"id": "c", "correctness": 2, "faithfulness": None},  # отказ: faithfulness не оценивается
        {"id": "z", "correctness": 2, "faithfulness": 2},  # нет в экспертной разметке
    ]
    review = {"a": {"correctness": 2, "faithfulness": 2}, "b": {"correctness": 2, "faithfulness": 2},
              "c": {"correctness": 1, "faithfulness": 2}}

    result = agreement(records, review)

    assert result["correctness"]["n"] == 3 and result["correctness"]["exact"] == pytest.approx(1 / 3, abs=1e-3)
    assert result["correctness"]["within_1"] == pytest.approx(2 / 3, abs=1e-3)
    assert (result["correctness"]["judge_stricter"], result["correctness"]["judge_lenient"]) == (1, 1)
    assert result["faithfulness"]["n"] == 2 and result["faithfulness"]["disagreements"] == ["a"]


def test_manual_review_covers_valid_ids_and_scale():
    from src.evaluation.agreement import load_review
    from src.evaluation.dataset import load_eval_set
    from tests.test_eval_set import EVAL_SET

    ids = {question.id for question in load_eval_set(EVAL_SET) if question.answerable}
    review = load_review()
    assert set(review) <= ids
    assert all(item[m] in (0, 1, 2) for item in review.values() for m in ("correctness", "faithfulness"))


def test_report_without_generation(records):
    retrieval_only = [{k: v for k, v in r.items() if k not in ("answer", "refused", "sources")} for r in records]
    text = render_report("r", {"top_k": 2}, summarize(retrieval_only, [1, 2], 2), retrieval_only, [1, 2])
    assert "## Retrieval" in text and "## Генерация" not in text
