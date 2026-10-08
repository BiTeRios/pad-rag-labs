"""Полный RAG: поиск контекста (retrieval + фильтры + reranker) → генерация ответа с источниками."""

import time
from dataclasses import dataclass

from src.generation.generator import Answer, AnswerGenerator
from src.retrieval.pipeline import RetrievalPipeline


@dataclass
class RAGResult:
    answer: Answer
    stages: dict[str, int]  # сколько chunks осталось после каждого шага поиска
    retrieval_s: float
    generation_s: float


class RAG:
    def __init__(self, retrieval: RetrievalPipeline, generator: AnswerGenerator):
        self.retrieval = retrieval
        self.generator = generator

    def ask(self, question: str, top_k: int | None = None, metadata: dict | None = None) -> RAGResult:
        started = time.perf_counter()
        found = self.retrieval.run(question, top_k, metadata)
        retrieved = time.perf_counter()
        answer = self.generator.generate(question, found.chunks)
        return RAGResult(answer, found.stages, retrieved - started, time.perf_counter() - retrieved)
