"""LLM-as-a-Judge: два независимых вызова.

- correctness — вопрос + эталон + ответ, без контекста. Судья выписывает ключевые факты эталона и
  статус каждого в ответе (есть / частично / нет / противоречит); оценка выводится из фактов правилом.
- faithfulness — контекст + ответ, без эталона. Как в RAGAS: судья разбивает ответ на утверждения
  и для каждого указывает фрагмент контекста, который его подтверждает. claim_support — доля подтверждённых утверждений.

Почему так: при оценке в один вызов с длинным контекстом модель отмечала факты эталона как «есть»,
потому что видела их в контексте, а не в ответе (калибровка: ответ «данные хранит kube-proxy» получил 2).
Шкала 0/1/2; ответ судьи ограничен JSON-схемой (structured output Ollama).
"""

import json
import logging
from dataclasses import dataclass, field

from src.tracing import Tracer

log = logging.getLogger(__name__)

STATUSES = ("есть", "частично", "нет", "противоречит")
CLAIM_STATUSES = ("подтверждено", "не подтверждено", "противоречит")

CORRECTNESS_SCHEMA = {
    "type": "object",
    "properties": {
        "facts": {
            "type": "array",
            "minItems": 1,
            "maxItems": 4,
            "items": {
                "type": "object",
                "properties": {"fact": {"type": "string"}, "status": {"type": "string", "enum": list(STATUSES)}},
                "required": ["fact", "status"],
            },
        },
        "correctness": {"type": "integer", "enum": [0, 1, 2]},
        "comment": {"type": "string"},
    },
    "required": ["facts", "correctness", "comment"],
}

FAITHFULNESS_SCHEMA = {
    "type": "object",
    "properties": {
        "claims": {
            "type": "array",
            "minItems": 1,
            "maxItems": 8,
            "items": {
                "type": "object",
                # порядок полей = порядок генерации: сначала номер фрагмента-подтверждения, потом статус.
                # Номер вместо цитаты: цитаты утраивали время судьи (≈23 с на ответ) при той же логике проверки.
                "properties": {
                    "claim": {"type": "string"},
                    "fragment": {"type": "integer", "minimum": 0},
                    "status": {"type": "string", "enum": list(CLAIM_STATUSES)},
                },
                "required": ["claim", "fragment", "status"],
            },
        },
        "faithfulness": {"type": "integer", "enum": [0, 1, 2]},
        "comment": {"type": "string"},
    },
    "required": ["claims", "faithfulness", "comment"],
}


@dataclass
class Verdict:
    correctness: int | None
    faithfulness: int | None
    comment: str
    facts: list[dict] = field(default_factory=list)
    unsupported_claims: list[str] = field(default_factory=list)
    claim_support: float | None = None  # доля подтверждённых утверждений ответа (0..1)


def correctness_from_facts(facts: list[dict], fallback: int) -> int:
    """Противоречие → 0; все факты есть → 2; есть хоть что-то верное → 1; иначе 0."""
    statuses = [fact["status"] for fact in facts if fact.get("status") in STATUSES]
    if not statuses:
        return fallback
    if "противоречит" in statuses:
        return 0
    if all(status == "есть" for status in statuses):
        return 2
    if any(status in ("есть", "частично") for status in statuses):
        return 1
    return 0


class LLMJudge:
    def __init__(self, llm, prompts: dict[str, dict], tracer: Tracer | None = None):
        """prompts: {"correctness": {"system", "user"}, "faithfulness": {"system", "user"}}."""
        self.llm = llm
        self.prompts = prompts
        self.tracer = tracer or Tracer()

    def judge(self, question: str, expected: str, context: str, answer: str) -> Verdict:
        correctness = self.correctness(question, expected, answer)
        faithfulness = self.faithfulness(question, context, answer)
        return Verdict(
            correctness=correctness.correctness,
            faithfulness=faithfulness.faithfulness,
            comment=f"{correctness.comment} | {faithfulness.comment}",
            facts=correctness.facts,
            unsupported_claims=faithfulness.unsupported_claims,
            claim_support=faithfulness.claim_support,
        )

    def correctness(self, question: str, expected: str, answer: str) -> Verdict:
        data = self._ask("correctness", CORRECTNESS_SCHEMA, question=question, expected=expected, answer=answer)
        if data is None:
            return Verdict(None, None, "судья correctness вернул некорректный JSON")
        facts = [fact for fact in data.get("facts", []) if isinstance(fact, dict)]
        return Verdict(correctness_from_facts(facts, data["correctness"]), None, str(data.get("comment", "")), facts=facts)

    def faithfulness(self, question: str, context: str, answer: str) -> Verdict:
        data = self._ask("faithfulness", FAITHFULNESS_SCHEMA, question=question, context=context or "(пусто)", answer=answer)
        if data is None:
            return Verdict(None, None, "судья faithfulness вернул некорректный JSON")
        claims = [c for c in data.get("claims", []) if isinstance(c, dict) and c.get("status") in CLAIM_STATUSES]
        unsupported = [str(c.get("claim", "")) for c in claims if c["status"] != "подтверждено"]
        support = round(1 - len(unsupported) / len(claims), 4) if claims else None
        # Все утверждения подтверждены → 2. Иначе оценку ставит модель: насколько важно неподтверждённое,
        # правилом не определить (жёсткое «есть утверждение → не выше 1» давало ложные снижения).
        score = 2 if claims and not unsupported else data["faithfulness"]
        return Verdict(None, score, str(data.get("comment", "")), unsupported_claims=unsupported, claim_support=support)

    def _ask(self, kind: str, schema: dict, **values) -> dict | None:
        prompt = self.prompts[kind]
        with self.tracer.observe(f"judge-{kind}", "evaluator") as span:
            response = self.llm.chat(prompt["system"], prompt["user"].format(**values), schema=schema)
            try:
                data = json.loads(response.text)
                score_key = kind
                data[score_key] = _score(data[score_key])
                span.update(output=data)
                return data
            except (ValueError, KeyError, TypeError) as error:
                log.warning("Судья %s вернул некорректный JSON (%s): %r", kind, error, response.text[:200])
                span.update(level="WARNING", status_message=f"некорректный JSON: {error}")
                return None


def _score(value) -> int:
    score = int(value)
    if score not in (0, 1, 2):
        raise ValueError(f"оценка вне шкалы: {score}")
    return score
