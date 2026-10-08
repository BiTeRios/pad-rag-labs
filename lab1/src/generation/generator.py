"""Генерация ответа: system prompt + вопрос + пронумерованный контекст → ответ со ссылками [n].

Защита от галлюцинаций:
- пустой контекст (фильтры отсекли всё) — LLM не вызывается, сразу отказ;
- промпт требует отвечать только по контексту и отказываться, если ответа в нём нет;
- источники берутся из ссылок [n], которые модель поставила в ответе.
"""

import re
from dataclasses import dataclass, field

from src.generation.llm import LLMResponse
from src.retrieval.filters import body_text

_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


@dataclass
class Answer:
    question: str
    text: str
    sources: list[dict]  # [{"n", "title", "heading", "url"}]
    refused: bool  # «информации недостаточно»: контекста нет или модель не нашла в нём ответ
    context: list[dict] = field(default_factory=list)  # chunks, переданные LLM
    llm: LLMResponse | None = None


class AnswerGenerator:
    def __init__(self, llm, system_prompt: str, user_template: str, no_context_answer: str, refusal_marker: str):
        self.llm = llm
        self.system_prompt = system_prompt
        self.user_template = user_template
        self.no_context_answer = no_context_answer
        self.refusal_marker = refusal_marker.lower()

    def generate(self, question: str, chunks: list[dict]) -> Answer:
        if not chunks:
            return Answer(question, self.no_context_answer, sources=[], refused=True)

        user = self.user_template.format(context=format_context(chunks), question=question)
        response = self.llm.chat(self.system_prompt, user)
        refused = self.refusal_marker in response.text.lower()
        sources = [] if refused else cited_sources(response.text, chunks)
        return Answer(question, response.text, sources, refused, context=chunks, llm=response)


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{n}] {chunk['heading']}\nИсточник: {chunk['url']}\n{body_text(chunk)}"
        for n, chunk in enumerate(chunks, 1)
    )


def cited_sources(text: str, chunks: list[dict]) -> list[dict]:
    """Фрагменты, на которые модель сослалась как [n] или [n, m]; без ссылок — весь контекст.

    Несколько chunks одной страницы дают один источник (по первому номеру).
    """
    cited = sorted({
        int(number)
        for group in _CITATION.findall(text)
        for number in group.split(",")
        if 1 <= int(number) <= len(chunks)
    })
    numbers = cited or list(range(1, len(chunks) + 1))
    sources, seen_urls = [], set()
    for n in numbers:
        chunk = chunks[n - 1]
        if chunk["url"] not in seen_urls:
            seen_urls.add(chunk["url"])
            sources.append({
                "n": n,
                "document_id": chunk["document_id"],
                "title": chunk["title"],
                "heading": chunk["heading"],
                "url": chunk["url"],
            })
    return sources
