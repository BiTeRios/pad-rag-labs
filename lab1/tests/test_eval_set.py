"""Проверка самого набора вопросов по реальному корпусу (пропускается, если корпус не собран)."""

import collections
from pathlib import Path

import pytest

from src.config import LAB_ROOT
from src.evaluation.dataset import TYPES, EvalQuestion, load_eval_set, validate
from src.preprocessing.pipeline import read_jsonl

EVAL_SET = LAB_ROOT / "experiments" / "eval_set.yaml"
DOCUMENTS = LAB_ROOT / "data" / "processed" / "documents.jsonl"


def test_eval_set_has_30_plus_questions_of_all_types():
    questions = load_eval_set(EVAL_SET)
    counts = collections.Counter(question.type for question in questions)
    assert len(questions) >= 30
    assert set(counts) == set(TYPES)
    assert all(count >= 5 for count in counts.values())
    assert all(question.match == "all" for question in questions if question.type == "multi_doc")


@pytest.mark.skipif(not DOCUMENTS.is_file(), reason="корпус не собран: запустите grabber и preprocessing")
def test_eval_set_matches_corpus():
    documents = {row["document_id"]: row["text"] for row in read_jsonl(DOCUMENTS)}
    assert validate(load_eval_set(EVAL_SET), documents) == []


def test_validate_reports_problems():
    questions = [
        EvalQuestion("a", "factual", "q", "e", ("doc1",), evidence=("missing phrase",)),
        EvalQuestion("b", "no_answer", "q", "e", (), absent=("pods",)),
        EvalQuestion("c", "unknown", "q", "e", ("doc2",)),
    ]
    problems = validate(questions, {"doc1": "Pods are `small`.", "doc3": "x"})
    assert any("evidence «missing phrase»" in p for p in problems)
    assert any("absent «pods»" in p for p in problems)
    assert any("неизвестный тип" in p for p in problems)
    assert any("нет документа doc2" in p for p in problems)


def test_validate_ignores_backticks_and_case():
    question = EvalQuestion("a", "specific", "q", "e", ("doc",), evidence=("nodeSelector is the simplest",))
    assert validate([question], {"doc": "`nodeSelector` is the  simplest form"}) == []
