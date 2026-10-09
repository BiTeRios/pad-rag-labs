"""Трассировка Langfuse на заглушке клиента: структура trace, generation с токенами, scores прогона."""

from contextlib import contextmanager
from types import SimpleNamespace

import pytest

from src.evaluation.judge import LLMJudge
from src.evaluation.langfuse_run import RunTracing, run_scores
from src.evaluation.runner import run_generation, run_judge, run_retrieval, summarize
from src.generation.generator import AnswerGenerator
from src.generation.llm import OllamaClient
from src.rag import RAG
from src.reranking.reranker import Reranker
from src.retrieval.pipeline import RetrievalPipeline
from src.tracing import Tracer, ascii_id, build_tracer
from tests.helpers import WordOverlapCrossEncoder
from tests.test_evaluation import CHUNKS, PROMPTS, QUESTIONS, REFUSAL, ScriptedLLM, StubRetriever
from tests.test_generation import OK, FakeSession


class FakeObservation:
    def __init__(self, name, as_type, trace_id, parent, fields):
        self.name, self.as_type, self.trace_id, self.parent = name, as_type, trace_id, parent
        self.id = f"obs-{name}"
        self.fields = dict(fields)
        self.trace_io = None

    def update(self, **fields):
        self.fields.update(fields)
        return self

    def set_trace_io(self, **io):
        self.trace_io = io
        return self


class FakeRunItems:
    def __init__(self):
        self.created = []

    def create(self, **item):
        self.created.append(item)
        return SimpleNamespace(dataset_run_id=f"run:{item['run_name']}")


class FakeApi:
    def __init__(self):
        self.dataset_run_items = FakeRunItems()


class FakeLangfuse:
    """Повторяет нужную часть API Langfuse: вложенность наблюдений, trace по seed, scores, datasets."""

    def __init__(self):
        self.observations: list[FakeObservation] = []
        self.scores: list[dict] = []
        self.items: list[dict] = []
        self.api = FakeApi()
        self.flushed = 0
        self._stack: list[FakeObservation] = []

    @contextmanager
    def start_as_current_observation(self, *, name, as_type, trace_context=None, **fields):
        parent = self._stack[-1] if self._stack else None
        if trace_context:
            trace_id = trace_context["trace_id"]
        else:
            trace_id = parent.trace_id if parent else f"trace-{len(self.observations)}"
        observation = FakeObservation(name, as_type, trace_id, parent, fields)
        self.observations.append(observation)
        self._stack.append(observation)
        try:
            yield observation
        finally:
            self._stack.pop()

    def create_trace_id(self, *, seed):
        return f"trace:{seed}"

    def create_score(self, **score):
        self.scores.append(score)

    def get_trace_url(self, *, trace_id):
        return f"http://langfuse/trace/{trace_id}"

    def create_dataset(self, **dataset):
        return SimpleNamespace(id=f"ds:{dataset['name']}")

    def create_dataset_item(self, **item):
        self.items.append(item)

    def flush(self):
        self.flushed += 1

    def named(self, name):
        return [obs for obs in self.observations if obs.name == name]


@pytest.fixture
def langfuse():
    client = FakeLangfuse()
    attributes = []

    @contextmanager
    def propagate(**values):
        attributes.append(values)
        yield

    client.attributes = attributes
    return client, Tracer(client, propagate, preview_chars=10)


def test_noop_tracer_changes_nothing():
    tracer = Tracer()
    with tracer.observe("x", input=1) as span:
        span.update(output=2)
    assert not tracer.enabled and span.trace_id is None and tracer.trace_url(None) is None
    tracer.score("hit@5", 1.0, trace_seed="run/f01")  # без клиента — ничего не делает


def test_build_tracer_is_disabled_without_keys(monkeypatch):
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    assert not build_tracer({"langfuse": {"enabled": True, "base_url": "http://x"}}).enabled
    assert not build_tracer({"langfuse": {"enabled": False}}).enabled
    assert not build_tracer({}).enabled


def test_rag_trace_contains_retrieval_steps_and_llm_generation(langfuse):
    client, tracer = langfuse
    pipeline = RetrievalPipeline(
        StubRetriever(CHUNKS), Reranker("fake-reranker", model=WordOverlapCrossEncoder()),
        top_k=1, candidates=5, tracer=tracer,
    )
    llm = OllamaClient("http://x", "qwen3:8b", think=False, session=FakeSession(OK), tracer=tracer)
    rag = RAG(pipeline, AnswerGenerator(llm, "S", "{context}\n{question}", REFUSAL, "недостаточно информации"), tracer)

    result = rag.ask("Что такое Pod?")

    root = client.named("rag-ask")[0]
    assert root.parent is None and result.trace_id == root.trace_id
    assert root.fields["output"]["answer"] == "Ответ [1]." and root.fields["metadata"]["llm_called"]
    assert root.trace_io["input"] == {"question": "Что такое Pod?"}
    assert client.attributes == [{"session_id": None, "trace_name": "rag-ask", "tags": None}]

    steps = [obs.name for obs in client.observations if obs.parent and obs.parent.name == "retrieval"]
    assert steps == ["vector-search", "filters", "rerank"]
    assert client.named("rerank")[0].fields["metadata"]["model"] == "fake-reranker"
    retrieval = client.named("retrieval")[0]
    assert retrieval.fields["metadata"]["stages"]["final"] == 1
    found = client.named("vector-search")[0].fields["output"]
    assert [chunk["text"] for chunk in found] == ["noise", "pod is sma"]  # текст обрезан до preview_chars
    assert found[1]["score"] == 0.8 and client.named("rerank")[0].fields["output"][0]["rerank_score"] is not None

    generation = client.named("ollama-chat")[0]
    assert generation.as_type == "generation" and generation.parent is root
    assert generation.fields["model"] == "qwen3:8b"
    assert generation.fields["model_parameters"] == {"temperature": 0.1, "num_ctx": 8192, "seed": 42, "think": False}
    assert generation.fields["usage_details"] == {"input": 1200, "output": 80}
    assert generation.fields["input"][1]["content"].endswith("Что такое Pod?")


def test_refusal_without_context_has_no_generation(langfuse):
    client, tracer = langfuse
    llm = OllamaClient("http://x", "qwen3:8b", session=FakeSession(OK), tracer=tracer)
    rag = RAG(RetrievalPipeline(StubRetriever({}), tracer=tracer),
              AnswerGenerator(llm, "S", "{context}\n{question}", REFUSAL, "недостаточно информации"), tracer)

    result = rag.ask("Как приготовить борщ?")

    assert result.answer.refused and client.named("ollama-chat") == []
    assert client.named("rag-ask")[0].fields["metadata"]["llm_called"] is False


def test_evaluation_run_is_session_with_trace_per_question_and_scores(langfuse):
    client, tracer = langfuse
    tracing = RunTracing(tracer, "E6/с_reranker", "k8s-eval", tags=["evaluation"])
    tracing.sync_dataset(QUESTIONS)
    records = run_retrieval(RetrievalPipeline(StubRetriever(CHUNKS), top_k=5, candidates=20, tracer=tracer),
                            QUESTIONS, [1, 2], tracing)
    llm = ScriptedLLM({"Что такое Pod?": "Pod — единица [2].", "Сколько стоит GKE?": "Около 70 долларов [1]."}, REFUSAL)
    run_generation(AnswerGenerator(llm, "S", "{context}\n{question}", REFUSAL, "недостаточно информации"),
                   records, 2, tracing)
    judge_llm = ScriptedLLM({}, '{"facts": [{"fact": "f", "status": "есть"}], "correctness": 2, "comment": "ok", '
                                '"claims": [{"claim": "c", "fragment": 1, "status": "подтверждено"}], "faithfulness": 2}')
    run_judge(LLMJudge(judge_llm, PROMPTS, tracer), records, tracing)
    tracing.report(records, summarize(records, [1, 2], 2), top_k=2)

    # три прохода одного вопроса — в одном trace, session и имя trace в ASCII
    f01 = [obs for obs in client.observations if obs.trace_id == "trace:E6/с_reranker/f01" and obs.parent is None]
    assert [obs.name for obs in f01] == ["eval-retrieval", "eval-generation", "eval-judge"]
    trace_attributes = [a for a in client.attributes if "session_id" in a]
    assert {a["session_id"] for a in trace_attributes} == {"eval-E6/s_reranker"}
    assert {a["trace_name"] for a in trace_attributes} == {"eval f01", "eval m01", "eval n01", "eval n02"}
    assert [obs.name for obs in client.observations if obs.parent and obs.parent.name == "eval-judge"] == \
        ["judge-correctness", "judge-faithfulness"] * 2

    scores = {(s["name"], s["trace_id"]): s["value"] for s in client.scores if s["trace_id"]}
    assert scores[("hit@2", "trace:E6/с_reranker/f01")] == 1 and scores[("reciprocal_rank", "trace:E6/с_reranker/f01")] == 0.5
    assert scores[("correctness", "trace:E6/с_reranker/f01")] == 1.0  # 2 из 2 → 1.0
    assert scores[("refusal_correct", "trace:E6/с_reranker/n01")] == 1.0
    assert scores[("refusal_correct", "trace:E6/с_reranker/n02")] == 0.0  # ответил на вопрос без ответа
    assert ("hit@2", "trace:E6/с_reranker/n01") not in scores  # у вопросов без ответа нет метрик retrieval

    session_scores = {s["name"] for s in client.scores if s["session_id"]}
    assert {"mrr", "hit@2", "correctness", "correct_refusal_rate"} <= session_scores
    assert [item["id"] for item in client.items] == ["k8s-eval-f01", "k8s-eval-m01", "k8s-eval-n01", "k8s-eval-n02"]
    # вопрос — item experiment: run item создаётся один раз, атрибуты experiment — на spans всех трёх проходов
    linked = client.api.dataset_run_items.created
    assert [item["dataset_item_id"] for item in linked] == ["k8s-eval-f01", "k8s-eval-m01", "k8s-eval-n01", "k8s-eval-n02"]
    assert linked[0] == {"run_name": "E6/с_reranker", "dataset_item_id": "k8s-eval-f01",
                         "trace_id": "trace:E6/с_reranker/f01", "observation_id": "obs-eval-retrieval"}
    experiments = [a["experiment"] for a in client.attributes if "experiment" in a]
    f01_experiment = [e for e in experiments if e["experiment_item_id"] == "k8s-eval-f01"]
    assert len(f01_experiment) == 3 and all(e == f01_experiment[0] for e in f01_experiment)
    assert f01_experiment[0]["experiment_id"] == "run:E6/с_reranker"
    assert f01_experiment[0]["experiment_dataset_id"] == "ds:k8s-eval"
    assert client.flushed == 1


def test_without_dataset_traces_are_not_linked_to_experiment(langfuse):
    client, tracer = langfuse
    tracing = RunTracing(tracer, "rejudge", tags=["rejudge"])
    with tracing.question("f01", "eval-judge"):
        pass
    assert client.api.dataset_run_items.created == [] and "experiment" not in client.attributes[0]


def test_langfuse_api_failure_does_not_break_evaluation(langfuse):
    client, tracer = langfuse

    def unavailable(**_):
        raise ConnectionError("langfuse down")

    client.create_dataset = unavailable
    tracing = RunTracing(tracer, "run", "k8s-eval")
    tracing.sync_dataset(QUESTIONS)
    records = run_retrieval(RetrievalPipeline(StubRetriever(CHUNKS), tracer=tracer), QUESTIONS, [1, 2], tracing)

    assert len(records) == 4 and tracing.dataset_id is None
    assert len(client.named("eval-retrieval")) == 4 and client.api.dataset_run_items.created == []


def test_run_scores_match_summary():
    summary = {"retrieval": {"overall": {"mrr": 0.9, "hit@5": 1.0, "recall@5": 0.95}},
               "judge": {"overall": {"correctness": 0.78, "faithfulness": 0.98}}}
    assert run_scores(summary, 5) == {"mrr": 0.9, "hit@5": 1.0, "recall@5": 0.95,
                                      "correctness": 0.78, "faithfulness": 0.98}


def test_ascii_id_transliterates_cyrillic():
    assert ascii_id("E6/без_reranker") == "E6/bez_reranker"
    assert ascii_id("eval-E7/с_порогом") == "eval-E7/s_porogom"
