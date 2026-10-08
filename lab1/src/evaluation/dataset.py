"""Набор вопросов для оценки: загрузка и проверка эталонов по корпусу."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml

TYPES = ("factual", "specific", "multi_doc", "context", "no_answer")
TYPE_NAMES = {
    "factual": "фактологические",
    "specific": "поиск конкретики",
    "multi_doc": "по нескольким документам",
    "context": "понимание контекста",
    "no_answer": "нет в базе",
}


@dataclass(frozen=True)
class EvalQuestion:
    id: str
    type: str
    question: str
    expected_answer: str
    relevant_docs: tuple[str, ...]
    match: str = "any"  # any — достаточно любого релевантного документа, all — нужны все
    evidence: tuple[str, ...] = field(default=())
    absent: tuple[str, ...] = field(default=())

    @property
    def answerable(self) -> bool:
        return self.type != "no_answer"


def load_eval_set(path: Path) -> list[EvalQuestion]:
    with path.open(encoding="utf-8") as file:
        rows = yaml.safe_load(file)
    return [
        EvalQuestion(
            id=row["id"],
            type=row["type"],
            question=row["question"],
            expected_answer=row["expected_answer"],
            relevant_docs=tuple(row.get("relevant_docs") or ()),
            match=row.get("match", "any"),
            evidence=tuple(row.get("evidence") or ()),
            absent=tuple(row.get("absent") or ()),
        )
        for row in rows
    ]


def validate(questions: list[EvalQuestion], documents: dict[str, str]) -> list[str]:
    """Проблемы набора: неизвестные типы, несуществующие документы, evidence нет в релевантных
    документах, absent-фраза есть в корпусе. documents — {document_id: текст}."""
    problems = []
    normalized = {doc_id: _normalize(text) for doc_id, text in documents.items()}
    ids = [question.id for question in questions]
    if len(ids) != len(set(ids)):
        problems.append("повторяющиеся id")
    for question in questions:
        prefix = f"{question.id}:"
        if question.type not in TYPES:
            problems.append(f"{prefix} неизвестный тип {question.type}")
        if question.match not in ("any", "all"):
            problems.append(f"{prefix} match должен быть any или all")
        if question.answerable and not question.relevant_docs:
            problems.append(f"{prefix} нет relevant_docs")
        if not question.answerable and question.relevant_docs:
            problems.append(f"{prefix} у no_answer не должно быть relevant_docs")
        missing = [doc for doc in question.relevant_docs if doc not in normalized]
        problems += [f"{prefix} нет документа {doc}" for doc in missing]
        relevant_texts = [normalized[doc] for doc in question.relevant_docs if doc in normalized]
        for phrase in question.evidence:
            if not any(_normalize(phrase) in text for text in relevant_texts):
                problems.append(f"{prefix} evidence «{phrase}» не найден в relevant_docs")
        for phrase in question.absent:
            found = [doc for doc, text in normalized.items() if _normalize(phrase) in text]
            if found:
                problems.append(f"{prefix} absent «{phrase}» есть в корпусе: {found[:3]}")
    return problems


def _normalize(text: str) -> str:
    return " ".join(text.replace("`", "").lower().split())
