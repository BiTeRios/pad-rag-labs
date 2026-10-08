import pytest
import requests

from src.config import load_config
from src.factory import build_generator
from src.generation.generator import AnswerGenerator, cited_sources, format_context
from src.generation.llm import LLMError, LLMResponse, OllamaClient
from src.rag import RAG
from src.retrieval.pipeline import RetrievalPipeline
from tests.helpers import make_chunk

NO_CONTEXT = "В документации недостаточно информации для ответа на этот вопрос."


def chunk(doc_id: str, index: int, body: str, heading: str) -> dict:
    return {**make_chunk(doc_id, index, f"{heading}\n\n{body}", score=0.9), "heading": heading, "title": heading}


CONTEXT = [
    chunk("pods", 0, "A Pod is the smallest deployable unit.", "Pods"),
    chunk("pods", 1, "Pods share network namespace.", "Pods > Networking"),
    chunk("services", 0, "A Service exposes Pods.", "Service"),
]


class FakeLLM:
    def __init__(self, text: str):
        self.text = text
        self.calls: list[tuple[str, str]] = []

    def chat(self, system: str, user: str) -> LLMResponse:
        self.calls.append((system, user))
        return LLMResponse(self.text, "fake", prompt_tokens=100, completion_tokens=20)


def generator(llm) -> AnswerGenerator:
    return AnswerGenerator(llm, "SYSTEM", "Контекст:\n{context}\n\nВопрос: {question}", NO_CONTEXT, "недостаточно информации")


def test_empty_context_refuses_without_calling_llm():
    llm = FakeLLM("anything")

    answer = generator(llm).generate("Как приготовить борщ?", [])

    assert answer.refused and answer.text == NO_CONTEXT and answer.sources == []
    assert llm.calls == [] and answer.llm is None


def test_context_is_numbered_with_heading_url_and_body_without_duplicate_heading():
    text = format_context(CONTEXT[:2])
    assert text == (
        "[1] Pods\nИсточник: https://kubernetes.io/docs/pods/\nA Pod is the smallest deployable unit.\n\n"
        "[2] Pods > Networking\nИсточник: https://kubernetes.io/docs/pods/\nPods share network namespace."
    )


def test_prompt_contains_context_and_question():
    llm = FakeLLM("Pod — минимальная единица [1].")

    generator(llm).generate("Что такое Pod?", CONTEXT)

    system, user = llm.calls[0]
    assert system == "SYSTEM"
    assert user.startswith("Контекст:\n[1] Pods") and user.endswith("Вопрос: Что такое Pod?")


def test_sources_come_from_citations_and_are_unique_per_page():
    answer = generator(FakeLLM("Pod — единица [2]. Service открывает доступ [3, 1]. [7]")).generate("q", CONTEXT)

    assert not answer.refused
    assert [(s["n"], s["url"]) for s in answer.sources] == [
        (1, "https://kubernetes.io/docs/pods/"),  # [1] и [2] — одна страница
        (3, "https://kubernetes.io/docs/services/"),
    ]


def test_answer_without_citations_lists_whole_context():
    assert [s["n"] for s in cited_sources("Ответ без ссылок.", CONTEXT)] == [1, 3]


def test_refusal_from_model_is_detected_and_has_no_sources():
    answer = generator(FakeLLM(f"«{NO_CONTEXT}»")).generate("Какой порт у kubelet?", CONTEXT)

    assert answer.refused and answer.sources == [] and len(answer.context) == 3


class FakeResponse:
    def __init__(self, status: int, payload: dict):
        self.status_code = status
        self.payload = payload
        self.text = str(payload)

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.requests: list[tuple[str, dict]] = []

    def post(self, url, json, timeout):
        self.requests.append((url, json))
        if self.error:
            raise self.error
        return self.response


OK = FakeResponse(200, {
    "message": {"content": "<think>hmm</think>Ответ [1].", "thinking": "reasoning"},
    "prompt_eval_count": 1200, "eval_count": 80, "total_duration": 2_500_000_000,
})


def test_ollama_payload_and_response_parsing():
    session = FakeSession(OK)
    client = OllamaClient("http://localhost:11434/", "qwen3:8b", temperature=0.2, num_ctx=4096, think=False, session=session)

    response = client.chat("sys", "user")

    url, payload = session.requests[0]
    assert url == "http://localhost:11434/api/chat"
    assert payload["model"] == "qwen3:8b" and payload["stream"] is False and payload["think"] is False
    assert payload["messages"] == [{"role": "system", "content": "sys"}, {"role": "user", "content": "user"}]
    assert payload["options"] == {"temperature": 0.2, "num_ctx": 4096, "seed": 42}
    assert (response.text, response.thinking) == ("Ответ [1].", "reasoning")
    assert (response.prompt_tokens, response.completion_tokens, response.seconds) == (1200, 80, 2.5)


def test_think_is_omitted_for_models_without_thinking():
    session = FakeSession(OK)
    OllamaClient("http://x", "gemma3:12b", think=None, session=session).chat("s", "u")
    assert "think" not in session.requests[0][1]


@pytest.mark.parametrize(
    ("session", "message"),
    [
        (FakeSession(FakeResponse(404, {"error": "model not found"})), "ollama pull qwen3:8b"),
        (FakeSession(FakeResponse(500, {"error": "out of memory"})), "out of memory"),
        (FakeSession(error=requests.ConnectionError("refused")), "запустите Ollama"),
        (FakeSession(error=requests.Timeout("slow")), "не ответила"),
    ],
)
def test_ollama_errors_become_llm_error(session, message):
    with pytest.raises(LLMError, match=message):
        OllamaClient("http://x", "qwen3:8b", session=session).chat("s", "u")


@pytest.mark.parametrize("name", ["strict", "basic"])
def test_prompts_from_config_load(name):
    gen = build_generator(load_config(), FakeLLM("ok"), name)
    assert "{" not in gen.system_prompt
    assert "{context}" in gen.user_template and "{question}" in gen.user_template
    if name == "strict":
        assert NO_CONTEXT in gen.system_prompt  # фраза отказа совпадает с той, что ищет детектор


class StubRetriever:
    def __init__(self, chunks):
        self.chunks = chunks

    def retrieve(self, query, top_k=None, filters=None):
        return self.chunks[:top_k]


def test_rag_ask_runs_retrieval_then_generation():
    rag = RAG(RetrievalPipeline(StubRetriever(CONTEXT), top_k=2), generator(FakeLLM("Pod — единица [1].")))

    result = rag.ask("Что такое Pod?")

    assert result.stages["final"] == 2 and len(result.answer.context) == 2
    assert result.answer.sources[0]["url"] == "https://kubernetes.io/docs/pods/"
    assert result.retrieval_s >= 0 and result.generation_s >= 0
