import math
from collections import Counter
from datetime import UTC, datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from analytics_service.models import AnswerRecord, Feedback, IndexUpdate, Registration
from rag_common.auth import Identity, current_identity, require_role
from rag_common.errors import BadRequest, Forbidden, NotFound, error_docs

router = APIRouter(prefix="/api", tags=["analytics"])


class FeedbackRequest(BaseModel):
    message_id: str
    rating: Literal[1, -1] = Field(description="1 — ответ полезен, -1 — нет")
    comment: str | None = None


class FeedbackOut(BaseModel):
    message_id: str
    rating: int
    comment: str | None
    created: bool = Field(description="false — оценка обновлена")


class Summary(BaseModel):
    period_days: int | None
    questions: int
    refusal_rate: float | None = Field(description="доля ответов «информации недостаточно»")
    llm_call_rate: float | None = Field(description="доля вопросов, где контекст найден и вызывалась LLM")
    degraded_rate: float | None = Field(description="доля ответов, где поиск работал без reranker")
    latency_ms: dict = Field(description="среднее и p95 полного ответа, только с вызовом LLM")
    feedback: dict
    top_sources: list[dict]
    users_registered: int
    last_index_update: dict | None


class QuestionRow(BaseModel):
    message_id: str
    question: str
    refused: bool
    sources: list[str]
    total_ms: int
    answered_at: datetime
    rating: int | None


@router.post("/feedback", response_model=FeedbackOut, status_code=201, summary="Оценить ответ",
             description="Оценивать можно только свой ответ. Ответ появляется в аналитике после события "
                         "question.answered: сразу после /api/chat/ask возможен 404 — повторите через секунду.",
             responses={200: {"model": FeedbackOut, "description": "оценка обновлена"}, **error_docs(400, 401, 403, 404, 422)})
async def feedback(body: FeedbackRequest, request: Request, identity: Identity = Depends(current_identity)):
    settings = request.app.state.settings
    if body.comment and len(body.comment) > settings.max_comment_chars:
        raise BadRequest(f"Комментарий длиннее {settings.max_comment_chars} символов", code="comment_too_long")
    async with request.app.state.sessions() as session:
        answer = await session.get(AnswerRecord, body.message_id)
        if answer is None:
            raise NotFound("Ответ не найден (или ещё не обработан аналитикой)", code="message_unknown")
        if answer.user_id != identity.user_id:
            raise Forbidden("Оценить можно только свой ответ")
        existing = await session.scalar(select(Feedback).where(
            Feedback.message_id == body.message_id, Feedback.user_id == identity.user_id))
        if existing:
            existing.rating, existing.comment = body.rating, body.comment
        else:
            session.add(Feedback(message_id=body.message_id, user_id=identity.user_id, rating=body.rating,
                                 comment=body.comment))
        await session.commit()
    result = FeedbackOut(message_id=body.message_id, rating=body.rating, comment=body.comment, created=existing is None)
    return JSONResponse(result.model_dump(), status_code=201 if existing is None else 200)


@router.get("/analytics/summary", response_model=Summary, summary="Сводка качества (admin)",
            responses=error_docs(401, 403))
async def summary(request: Request, days: int | None = Query(None, ge=1, le=365, description="за последние N дней"),
                  _: Identity = Depends(require_role("admin"))):
    since = datetime.now(UTC) - timedelta(days=days) if days else None
    async with request.app.state.sessions() as session:
        query = select(AnswerRecord)
        if since:
            query = query.where(AnswerRecord.answered_at >= since)
        answers = list(await session.scalars(query))
        ids = [answer.message_id for answer in answers]
        ratings = [row.rating for row in await session.scalars(select(Feedback).where(Feedback.message_id.in_(ids)))] if ids else []
        users = await session.scalar(select(func.count()).select_from(Registration))
        last = await session.scalar(select(IndexUpdate).order_by(IndexUpdate.occurred_at.desc()).limit(1))

    answered = [answer.total_ms for answer in answers if answer.llm_called]
    sources = Counter(document for answer in answers for document in answer.sources)
    return Summary(
        period_days=days,
        questions=len(answers),
        refusal_rate=_rate(answers, lambda a: a.refused),
        llm_call_rate=_rate(answers, lambda a: a.llm_called),
        degraded_rate=_rate(answers, lambda a: bool(a.degraded)),
        latency_ms={"mean": round(sum(answered) / len(answered)) if answered else None, "p95": _p95(answered)},
        feedback={"count": len(ratings), "positive": ratings.count(1), "negative": ratings.count(-1),
                  "positive_rate": round(ratings.count(1) / len(ratings), 3) if ratings else None},
        top_sources=[{"document_id": doc, "citations": n} for doc, n in sources.most_common(request.app.state.settings.top_sources)],
        users_registered=users,
        last_index_update=None if last is None else {
            "trigger": last.trigger, "collection": last.collection, "added": last.added, "updated": last.updated,
            "deleted": last.deleted, "chunks_indexed": last.chunks_indexed, "duration_s": last.duration_s,
            "occurred_at": last.occurred_at.isoformat()},
    )


@router.get("/analytics/questions", response_model=list[QuestionRow], summary="Последние вопросы (admin)",
            description="refused=true — вопросы без ответа в документации: подсказка, чем пополнить корпус.",
            responses=error_docs(401, 403))
async def questions(request: Request, refused: bool | None = None,
                    rating: int | None = Query(None, description="1 или -1: ответы с такой оценкой"),
                    limit: int = Query(50, ge=1, le=200), _: Identity = Depends(require_role("admin"))):
    if rating not in (None, 1, -1):  # Literal в query-строке не приводится из "-1", проверяем вручную
        raise BadRequest("rating: 1 или -1", code="invalid_rating")
    query = (select(AnswerRecord, Feedback.rating)
             .outerjoin(Feedback, Feedback.message_id == AnswerRecord.message_id)
             .order_by(AnswerRecord.answered_at.desc()).limit(limit))
    if refused is not None:
        query = query.where(AnswerRecord.refused == refused)
    if rating is not None:
        query = query.where(Feedback.rating == rating)
    async with request.app.state.sessions() as session:
        rows = (await session.execute(query)).all()
    return [QuestionRow(message_id=a.message_id, question=a.question, refused=a.refused, sources=a.sources,
                        total_ms=a.total_ms, answered_at=a.answered_at, rating=r) for a, r in rows]


def _rate(items: list, predicate) -> float | None:
    return round(sum(1 for item in items if predicate(item)) / len(items), 3) if items else None


def _p95(values: list[int]) -> int | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(0.95 * len(ordered)) - 1)]
