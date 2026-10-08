"""Сценарий «вопрос → ответ»: retrieval-service → LLM → история в своей БД → событие question.answered."""

import logging
import time
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from chat_service.generator import AnswerGenerator
from chat_service.models import Conversation, Message
from rag_common.auth import Identity
from rag_common.errors import BadRequest, NotFound
from rag_common.events import publish_safely
from rag_common.http import ServiceClient

log = logging.getLogger(__name__)

EVENT_QUESTION_ANSWERED = "question.answered"


class ChatService:
    def __init__(self, sessions, retrieval: ServiceClient, generator: AnswerGenerator, bus, settings):
        self.sessions = sessions
        self.retrieval = retrieval
        self.generator = generator
        self.bus = bus
        self.settings = settings

    async def ask(self, identity: Identity, question: str, conversation_id: str | None) -> Message:
        question = question.strip()
        if not question or len(question) > self.settings.max_question_chars:
            raise BadRequest(f"Вопрос должен быть от 1 до {self.settings.max_question_chars} символов", code="invalid_question")
        if conversation_id:
            await self._conversation(identity, conversation_id)  # чужой или несуществующий диалог → 404 до поиска

        started = time.perf_counter()
        found = await self.retrieval.post("/api/search", json={"query": question}, headers=identity.headers())
        retrieved = time.perf_counter()
        answer = await self.generator.generate(question, found["chunks"])
        finished = time.perf_counter()
        timings = {"retrieval": round((retrieved - started) * 1000), "generation": round((finished - retrieved) * 1000),
                   "total": round((finished - started) * 1000)}

        async with self.sessions() as session:
            if conversation_id:
                conversation = await session.get(Conversation, conversation_id)
                conversation.updated_at = datetime.now(UTC)
            else:
                conversation = Conversation(user_id=identity.user_id, title=question[:200])
                session.add(conversation)
                await session.flush()
            message = Message(
                conversation_id=conversation.id, user_id=identity.user_id, question=question, answer=answer.text,
                refused=answer.refused, sources=answer.sources, context_ids=answer.context_ids,
                model=answer.llm.model if answer.llm else None, prompt=self.settings.prompt_name,
                stages=found["stages"], timings_ms=timings, degraded=found["degraded"],
            )
            session.add(message)
            await session.commit()

        log.info("Ответ готов", extra={"message_id": message.id, "refused": answer.refused, "total_ms": timings["total"],
                                       "llm_called": answer.llm is not None})
        await publish_safely(self.bus, EVENT_QUESTION_ANSWERED, {
            "message_id": message.id, "conversation_id": message.conversation_id, "user_id": identity.user_id,
            "question": question, "refused": answer.refused, "llm_called": answer.llm is not None,
            "sources": [source["document_id"] for source in answer.sources], "model": message.model,
            "prompt": message.prompt, "timings_ms": timings, "degraded": found["degraded"],
            "context_chunks": len(answer.context_ids),
        })
        return message

    async def conversations(self, identity: Identity, limit: int, offset: int) -> tuple[list[Conversation], int]:
        query = select(Conversation).where(Conversation.user_id == identity.user_id)
        async with self.sessions() as session:
            total = await session.scalar(select(func.count()).select_from(query.subquery()))
            items = await session.scalars(query.order_by(Conversation.updated_at.desc()).limit(limit).offset(offset))
            return list(items), total

    async def conversation(self, identity: Identity, conversation_id: str) -> Conversation:
        return await self._conversation(identity, conversation_id, with_messages=True)

    async def delete(self, identity: Identity, conversation_id: str) -> None:
        async with self.sessions() as session:
            conversation = await self._conversation(identity, conversation_id, session=session)
            await session.delete(conversation)
            await session.commit()

    async def _conversation(self, identity: Identity, conversation_id: str, *, with_messages=False, session=None):
        query = select(Conversation).where(Conversation.id == conversation_id)
        if with_messages:
            query = query.options(selectinload(Conversation.messages))
        if session is None:
            async with self.sessions() as session:
                conversation = await session.scalar(query)
        else:
            conversation = await session.scalar(query)
        # Чужой диалог неотличим от несуществующего: id не раскрывает, что диалог есть. Admin видит все.
        if conversation is None or (conversation.user_id != identity.user_id and not identity.is_admin):
            raise NotFound("Диалог не найден")
        return conversation
