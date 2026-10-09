"""Прогон набора вопросов в три прохода: retrieval → генерация → судья.

Проходы разделены, чтобы LLM-генератор и LLM-судья не вытесняли друг друга из видеопамяти
на каждом вопросе: каждая модель загружается один раз.
"""

import logging
import time

from src.evaluation.dataset import TYPES, EvalQuestion
from src.evaluation.judge import LLMJudge
from src.evaluation.langfuse_run import RunTracing
from src.evaluation.metrics import average, retrieval_metrics
from src.generation.generator import AnswerGenerator, format_context
from src.retrieval.pipeline import RetrievalPipeline

log = logging.getLogger(__name__)


def run_retrieval(pipeline: RetrievalPipeline, questions: list[EvalQuestion], k_values: list[int],
                  tracing: RunTracing | None = None) -> list[dict]:
    """Поиск с top_k = max(K): метрики для меньших K считаются по префиксу того же списка."""
    tracing = tracing or RunTracing()
    max_k = max(k_values)
    records = []
    for question in questions:
        started = time.perf_counter()
        with tracing.question(question.id, "eval-retrieval", input={"question": question.question}):
            result = pipeline.run(question.question, top_k=max_k)
        record = {
            "id": question.id,
            "type": question.type,
            "question": question.question,
            "expected_answer": question.expected_answer,
            "relevant_docs": list(question.relevant_docs),
            "match": question.match,
            "answerable": question.answerable,
            "stages": result.stages,
            "retrieval_s": round(time.perf_counter() - started, 3),
            "retrieved": [
                {
                    "rank": rank,
                    "document_id": chunk["document_id"],
                    "heading": chunk["heading"],
                    "score": round(chunk["score"], 4),
                    "rerank_score": round(chunk["rerank_score"], 4) if "rerank_score" in chunk else None,
                }
                for rank, chunk in enumerate(result.chunks, 1)
            ],
            "_chunks": result.chunks,  # для генерации; в файлы не пишется
        }
        if question.answerable:
            ranked = [chunk["document_id"] for chunk in result.chunks]
            record["metrics"] = retrieval_metrics(ranked, set(question.relevant_docs), question.match, k_values)
        record["empty_context"] = not result.chunks
        records.append(record)
        log.info("retrieval %s: %d chunks", question.id, len(result.chunks))
    return records


def run_generation(generator: AnswerGenerator, records: list[dict], top_k: int,
                   tracing: RunTracing | None = None) -> None:
    """Ответ по первым top_k chunks — ровно тот контекст, который получила бы LLM в RAG."""
    tracing = tracing or RunTracing()
    for record in records:
        context = record["_chunks"][:top_k]
        started = time.perf_counter()
        with tracing.question(record["id"], "eval-generation", input={"question": record["question"]}) as span:
            answer = generator.generate(record["question"], context)
            span.update(output={"answer": answer.text, "refused": answer.refused})
            span.set_trace_io(input={"question": record["question"], "expected": record["expected_answer"]},
                              output={"answer": answer.text, "sources": [s["url"] for s in answer.sources]})
        record.update(
            answer=answer.text,
            refused=answer.refused,
            sources=answer.sources,
            context_ids=[chunk["chunk_id"] for chunk in context],
            generation_s=round(time.perf_counter() - started, 3),
            llm_called=answer.llm is not None,
            context_text=format_context(context) if context else "",  # сохраняется: нужен для --rejudge
        )
        if record["answerable"]:
            cited = {source["document_id"] for source in answer.sources}
            record["citation_hit"] = None if answer.refused else float(bool(cited & set(record["relevant_docs"])))
        log.info("generation %s: refused=%s", record["id"], answer.refused)


def run_judge(judge: LLMJudge, records: list[dict], tracing: RunTracing | None = None) -> None:
    """correctness и faithfulness в шкале 0..2.

    - Отказ на вопрос без ответа — верно (2), на вопрос с ответом — неверно (0); судья не нужен.
    - Ответ на вопрос без ответа — неверно (0); судья оценивает только faithfulness.
    """
    tracing = tracing or RunTracing()
    for record in records:
        if record["refused"]:
            record.update(correctness=2 if not record["answerable"] else 0, faithfulness=None, judge_comment="отказ")
            continue
        with tracing.question(record["id"], "eval-judge") as span:
            verdict = judge.judge(record["question"], record["expected_answer"], record["context_text"], record["answer"])
            span.update(output={"correctness": verdict.correctness, "faithfulness": verdict.faithfulness,
                                "comment": verdict.comment})
        record.update(
            correctness=verdict.correctness if record["answerable"] else 0,
            faithfulness=verdict.faithfulness,
            judge_comment=verdict.comment,
            judge_facts=verdict.facts,  # разбор судьи: факты эталона и их статус в ответе
            judge_unsupported=verdict.unsupported_claims,
            claim_support=verdict.claim_support,
        )
        log.info("judge %s: correctness=%s faithfulness=%s", record["id"], verdict.correctness, verdict.faithfulness)


def summarize(records: list[dict], k_values: list[int], top_k: int) -> dict:
    answerable = [record for record in records if record["answerable"]]
    unanswerable = [record for record in records if not record["answerable"]]
    metric_keys = ["rr"] + [f"{name}@{k}" for k in k_values for name in ("hit", "recall", "precision")]

    def retrieval_block(rows: list[dict]) -> dict:
        flat = [row["metrics"] for row in rows]
        block = {key: average(flat, key) for key in metric_keys}
        block["mrr"] = block.pop("rr")
        return block

    summary = {
        "questions": len(records),
        "retrieval": {
            "overall": retrieval_block(answerable),
            "by_type": {
                kind: retrieval_block([r for r in answerable if r["type"] == kind])
                for kind in TYPES if kind != "no_answer" and any(r["type"] == kind for r in answerable)
            },
            "no_answer_empty_context_rate": average([{"v": float(r["empty_context"])} for r in unanswerable], "v"),
            # фильтры отсекли всё на вопросе с ответом → гарантированный ложный отказ
            "answerable_empty_context_rate": average([{"v": float(r["empty_context"])} for r in answerable], "v"),
        },
        "latency_s": {"retrieval": average(records, "retrieval_s")},
    }

    if records and "answer" in records[0]:
        summary["generation"] = {
            "top_k": top_k,
            "false_refusal_rate": average([{"v": float(r["refused"])} for r in answerable], "v"),
            "correct_refusal_rate": average([{"v": float(r["refused"])} for r in unanswerable], "v"),
            "citation_hit_rate": average(answerable, "citation_hit"),
            "llm_calls": sum(record["llm_called"] for record in records),
        }
        summary["latency_s"]["generation"] = average([r for r in records if r["llm_called"]], "generation_s")

    if records and "correctness" in records[0]:
        def judged(rows: list[dict]) -> dict:
            correctness = average(rows, "correctness")
            faithfulness = average(rows, "faithfulness")
            return {
                "correctness": round(correctness / 2, 4) if correctness is not None else None,
                "faithfulness": round(faithfulness / 2, 4) if faithfulness is not None else None,
                "claim_support": average(rows, "claim_support"),
                "n": len(rows),
            }

        summary["judge"] = {
            "answerable": judged(answerable),
            "no_answer": judged(unanswerable),
            "overall": judged(records),
            "by_type": {kind: judged([r for r in records if r["type"] == kind]) for kind in TYPES},
            "judge_failures": sum(
                1 for r in records if not r["refused"] and r["faithfulness"] is None
            ),
        }
    return summary
