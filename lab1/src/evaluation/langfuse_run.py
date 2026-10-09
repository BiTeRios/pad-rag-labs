"""Прогон evaluation в Langfuse.

- Прогон — session (`eval-<имя прогона>`), вопрос — trace: три прохода (retrieval → генерация → судья)
  попадают в один trace по seed «прогон/id вопроса».
- Метрики retrieval, отказы, citation hit и оценки судьи — scores trace; итоги прогона — scores session.
- Набор вопросов — dataset `evaluation.langfuse_dataset`, прогон — experiment (dataset run) с тем же именем:
  в Langfuse прогоны экспериментов сравниваются по scores бок о бок и по каждому вопросу.
  Trace привязывается к experiment так же, как в `Langfuse.run_experiment`: item run в dataset +
  атрибуты experiment на spans вопроса. Свой цикл вместо run_experiment нужен из-за трёх проходов.
"""

import logging
from contextlib import contextmanager

from src.evaluation.dataset import EvalQuestion
from src.tracing import Tracer, ascii_id

log = logging.getLogger(__name__)


class RunTracing:
    def __init__(self, tracer: Tracer | None = None, run_name: str = "", dataset: str | None = None,
                 tags: list[str] | None = None):
        self.tracer = tracer or Tracer()
        self.run_name = run_name
        self.session_id = ascii_id(f"eval-{run_name}")
        self.dataset = dataset
        self.tags = tags or []
        self.dataset_id: str | None = None
        self._items: dict[str, dict] = {}  # id вопроса → атрибуты experiment (после первого прохода)

    def _seed(self, question_id: str) -> str:
        return f"{self.run_name}/{question_id}"

    @contextmanager
    def question(self, question_id: str, step: str, **fields):
        """Проход по вопросу: span в trace вопроса; вложенные spans (поиск, LLM, судья) — внутри."""
        with self.tracer.observe(
            step, "chain", trace_seed=self._seed(question_id), session_id=self.session_id,
            trace_name=ascii_id(f"eval {question_id}"), tags=self.tags, **fields,
        ) as span:
            experiment = self._experiment(question_id, span)
            if experiment is None:
                yield span
            else:
                with self.tracer.propagate(experiment=experiment):
                    yield span

    def _experiment(self, question_id: str, span) -> dict | None:
        """Атрибуты experiment для spans вопроса; item run создаётся на первом проходе."""
        if not (self.dataset_id and self.tracer.experiments):
            return None
        if question_id not in self._items:
            try:
                run_item = self.tracer.client.api.dataset_run_items.create(
                    run_name=self.run_name,
                    dataset_item_id=self._item_id(question_id),
                    trace_id=span.trace_id,
                    observation_id=span.id,
                )
            except Exception as error:  # Langfuse недоступен: прогон продолжается, traces — без experiment
                log.warning("Langfuse: experiment %s не записан (%s)", self.run_name, error)
                self.dataset_id = None
                return None
            self._items[question_id] = {
                "experiment_id": run_item.dataset_run_id,
                "experiment_name": self.run_name,
                "experiment_metadata": None,
                "experiment_dataset_id": self.dataset_id,
                "experiment_item_id": self._item_id(question_id),
                "experiment_item_metadata": None,
                "experiment_item_root_observation_id": span.id,
            }
        return self._items[question_id]

    def sync_dataset(self, questions: list[EvalQuestion]) -> None:
        """Вопросы набора → items dataset (upsert по id: повторный запуск не создаёт дублей)."""
        client = self.tracer.client
        if client is None or not self.dataset:
            return
        try:
            dataset = client.create_dataset(name=self.dataset,
                                            description="Вопросы evaluation Lab1 (experiments/eval_set.yaml)")
            for question in questions:
                client.create_dataset_item(
                    dataset_name=self.dataset,
                    id=self._item_id(question.id),
                    input={"question": question.question},
                    expected_output={"answer": question.expected_answer, "relevant_docs": list(question.relevant_docs)},
                    metadata={"id": question.id, "type": question.type, "answerable": question.answerable},
                )
        except Exception as error:  # без dataset прогон всё равно пишется: session, traces, scores
            log.warning("Langfuse: dataset %s не обновлён (%s) — прогон без experiment", self.dataset, error)
            return
        self.dataset_id = dataset.id

    def report(self, records: list[dict], summary: dict, top_k: int) -> None:
        """Scores по вопросам (trace) и итоги прогона (session)."""
        if not self.tracer.enabled:
            return
        for record in records:
            self._score_question(record, top_k)
        for name, value in run_scores(summary, top_k).items():
            self.tracer.score(name, value, session_id=self.session_id)
        self.tracer.flush()
        log.info("Langfuse: прогон %s — session %s, %d trace", self.run_name, self.session_id, len(records))

    def _score_question(self, record: dict, top_k: int) -> None:
        score = self.tracer.score
        seed = self._seed(record["id"])
        metrics = record.get("metrics") or {}
        for name in (f"hit@{top_k}", f"recall@{top_k}", f"precision@{top_k}"):
            score(name, metrics.get(name), trace_seed=seed)
        score("reciprocal_rank", metrics.get("rr"), trace_seed=seed)
        if "refused" in record:
            score("refused", float(record["refused"]), trace_seed=seed, data_type="BOOLEAN")
            score("refusal_correct", float(record["refused"] != record["answerable"]), trace_seed=seed,
                  data_type="BOOLEAN")
            score("citation_hit", record.get("citation_hit"), trace_seed=seed)
        if "correctness" in record:
            comment = record.get("judge_comment")
            score("correctness", _half(record["correctness"]), trace_seed=seed, comment=comment)
            score("faithfulness", _half(record["faithfulness"]), trace_seed=seed, comment=comment)
            score("claim_support", record.get("claim_support"), trace_seed=seed)

    def _item_id(self, question_id: str) -> str:
        return ascii_id(f"{self.dataset}-{question_id}")


def run_scores(summary: dict, top_k: int) -> dict[str, float | None]:
    """Итоги прогона: те же числа, что в summary.json."""
    overall = summary["retrieval"]["overall"]
    scores = {"mrr": overall["mrr"], f"hit@{top_k}": overall[f"hit@{top_k}"], f"recall@{top_k}": overall[f"recall@{top_k}"]}
    if "generation" in summary:
        generation = summary["generation"]
        scores.update(correct_refusal_rate=generation["correct_refusal_rate"],
                      false_refusal_rate=generation["false_refusal_rate"],
                      citation_hit_rate=generation["citation_hit_rate"])
    if "judge" in summary:
        judged = summary["judge"]["overall"]
        scores.update(correctness=judged["correctness"], faithfulness=judged["faithfulness"])
    return scores


def _half(value: int | None) -> float | None:
    """Шкала судьи 0..2 → 0..1, как в summary.json."""
    return None if value is None else value / 2
