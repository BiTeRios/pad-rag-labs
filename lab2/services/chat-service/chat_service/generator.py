"""Ответ на вопрос по найденному контексту (логика Lab1, src/generation/generator.py).

Защита от галлюцинаций:
- контекст пуст (фильтры retrieval-service отсекли всё) — LLM не вызывается, сразу отказ;
- промпт требует отвечать только по контексту и отказываться, если ответа в нём нет;
- источники — фрагменты, на которые модель сослалась как [n].
"""

import re
from dataclasses import dataclass, field

from chat_service.llm import LLMResponse

_CITATION = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


@dataclass
class Answer:
    text: str
    sources: list[dict]
    refused: bool
    llm: LLMResponse | None = None
    context_ids: list[str] = field(default_factory=list)


class AnswerGenerator:
    def __init__(self, llm, system_prompt: str, user_template: str, no_context_answer: str, refusal_marker: str):
        self.llm = llm
        self.system_prompt = system_prompt
        self.user_template = user_template
        self.no_context_answer = no_context_answer
        self.refusal_marker = refusal_marker.lower()

    async def generate(self, question: str, chunks: list[dict]) -> Answer:
        if not chunks:
            return Answer(self.no_context_answer, [], refused=True)
        user = self.user_template.format(context=format_context(chunks), question=question)
        response = await self.llm.chat(self.system_prompt, user)
        refused = self.refusal_marker in response.text.lower()
        sources = [] if refused else cited_sources(response.text, chunks)
        return Answer(response.text, sources, refused, response, [chunk["chunk_id"] for chunk in chunks])


def body_text(chunk: dict) -> str:
    """Текст chunk без префикса «Title > Section\\n\\n» (путь заголовков выводится отдельно)."""
    return chunk["text"].removeprefix(f"{chunk.get('heading', '')}\n\n").strip()


def format_context(chunks: list[dict]) -> str:
    return "\n\n".join(
        f"[{n}] {chunk['heading']}\nИсточник: {chunk['url']}\n{body_text(chunk)}" for n, chunk in enumerate(chunks, 1)
    )


def cited_sources(text: str, chunks: list[dict]) -> list[dict]:
    """Фрагменты, на которые сослалась модель ([n] или [n, m]); без ссылок — весь контекст.

    Несколько chunks одной страницы дают один источник; refs — все номера [n] этой страницы, чтобы клиент мог
    связать с источником любую ссылку ответа, а не только первую.
    """
    cited = sorted({
        int(number) for group in _CITATION.findall(text) for number in group.split(",") if 1 <= int(number) <= len(chunks)
    })
    by_url: dict[str, dict] = {}
    for n in cited or range(1, len(chunks) + 1):
        chunk = chunks[n - 1]
        if chunk["url"] in by_url:
            by_url[chunk["url"]]["refs"].append(n)
        else:
            by_url[chunk["url"]] = {"n": n, "refs": [n], "document_id": chunk["document_id"], "title": chunk["title"],
                                    "heading": chunk["heading"], "url": chunk["url"]}
    return list(by_url.values())
