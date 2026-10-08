"""Обработка событий: question.answered, index.updated, user.registered → таблицы аналитики."""

import logging
from datetime import datetime

from sqlalchemy.exc import IntegrityError

from analytics_service.models import AnswerRecord, IndexUpdate, Registration
from rag_common.events import Event

log = logging.getLogger(__name__)

ROUTING_KEYS = ("question.answered", "index.updated", "user.registered")


class Projector:
    def __init__(self, sessions):
        self.sessions = sessions

    async def handle(self, event: Event) -> None:
        builder = {
            "question.answered": self._answer,
            "index.updated": self._index_update,
            "user.registered": self._registration,
        }.get(event.type)
        if builder is None:
            log.warning("Неизвестное событие %s пропущено", event.type)
            return
        async with self.sessions() as session:
            session.add(builder(event, datetime.fromisoformat(event.occurred_at)))
            try:
                await session.commit()
            except IntegrityError:  # повторная доставка: событие уже учтено
                await session.rollback()
                log.info("Событие %s (%s) уже учтено", event.type, event.event_id)

    @staticmethod
    def _answer(event: Event, at: datetime) -> AnswerRecord:
        p = event.payload
        timings = p.get("timings_ms", {})
        return AnswerRecord(
            message_id=p["message_id"], event_id=event.event_id, user_id=p["user_id"], question=p["question"],
            refused=p["refused"], llm_called=p.get("llm_called", True), sources=p.get("sources", []),
            model=p.get("model"), prompt=p.get("prompt"), total_ms=timings.get("total", 0),
            retrieval_ms=timings.get("retrieval", 0), generation_ms=timings.get("generation", 0),
            degraded=p.get("degraded", []), answered_at=at,
        )

    @staticmethod
    def _index_update(event: Event, at: datetime) -> IndexUpdate:
        p = event.payload
        return IndexUpdate(
            event_id=event.event_id, trigger=p.get("trigger", "event"), collection=p.get("collection"),
            added=p.get("added", 0), updated=p.get("updated", 0), deleted=p.get("deleted", 0),
            chunks_indexed=p.get("chunks_indexed", 0), duration_s=p.get("duration_s"), occurred_at=at,
        )

    @staticmethod
    def _registration(event: Event, at: datetime) -> Registration:
        return Registration(event_id=event.event_id, user_id=event.payload["user_id"], role=event.payload["role"],
                            occurred_at=at)
