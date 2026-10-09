"""Полный RAG: поиск контекста (retrieval + фильтры + reranker) → генерация ответа с источниками."""

import time
from dataclasses import dataclass

from src.generation.generator import Answer, AnswerGenerator
from src.retrieval.pipeline import RetrievalPipeline
from src.tracing import Tracer


@dataclass
class RAGResult:
    answer: Answer
    stages: dict[str, int]  # сколько chunks осталось после каждого шага поиска
    retrieval_s: float
    generation_s: float
    trace_id: str | None = None  # trace в Langfuse; None — трассировка выключена


class RAG:
    def __init__(self, retrieval: RetrievalPipeline, generator: AnswerGenerator, tracer: Tracer | None = None):
        self.retrieval = retrieval
        self.generator = generator
        self.tracer = tracer or Tracer()

    def ask(self, question: str, top_k: int | None = None, metadata: dict | None = None) -> RAGResult:
        with self.tracer.observe("rag-ask", "chain", trace_name="rag-ask", input={"question": question}) as trace:
            started = time.perf_counter()
            found = self.retrieval.run(question, top_k, metadata)
            retrieved = time.perf_counter()
            answer = self.generator.generate(question, found.chunks)
            result = RAGResult(answer, found.stages, retrieved - started, time.perf_counter() - retrieved, trace.trace_id)
            output = {"answer": answer.text, "refused": answer.refused, "sources": [s["url"] for s in answer.sources]}
            trace.update(output=output, metadata={
                "stages": found.stages,
                "llm_called": answer.llm is not None,
                "retrieval_s": round(result.retrieval_s, 3),
                "generation_s": round(result.generation_s, 3),
            })
            trace.set_trace_io(input={"question": question}, output=output)
        return result
