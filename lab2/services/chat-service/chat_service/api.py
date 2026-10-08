from datetime import datetime

from fastapi import APIRouter, Depends, Query, Request, Response
from pydantic import BaseModel, ConfigDict, Field

from rag_common.auth import Identity, current_identity
from rag_common.errors import error_docs

router = APIRouter(prefix="/api/chat", tags=["chat"])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, examples=["Как ограничить потребление памяти контейнером?"])
    conversation_id: str | None = Field(None, description="продолжить диалог; без него создаётся новый")


class Source(BaseModel):
    n: int = Field(description="номер фрагмента в ответе: [n]")
    document_id: str
    title: str
    heading: str
    url: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    question: str
    answer: str
    refused: bool = Field(description="«информации недостаточно»: ответа нет в документации")
    sources: list[Source]
    model: str | None = Field(description="LLM; пусто — LLM не вызывалась (контекст не найден)")
    prompt: str
    stages: dict[str, int]
    timings_ms: dict[str, int]
    degraded: list[str]
    created_at: datetime


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationFull(ConversationOut):
    messages: list[MessageOut]


class ConversationPage(BaseModel):
    items: list[ConversationOut]
    total: int


@router.post("/ask", response_model=MessageOut, summary="Вопрос → ответ с источниками",
             description="Поиск контекста (retrieval-service) и ответ LLM по нему. Если ответа в документации нет, "
                         "refused = true. Ответ сохраняется в историю, публикуется событие question.answered.",
             responses=error_docs(400, 401, 404, 422, 502, 504))
async def ask(body: AskRequest, request: Request, identity: Identity = Depends(current_identity)):
    return await request.app.state.chat.ask(identity, body.question, body.conversation_id)


@router.get("/conversations", response_model=ConversationPage, summary="Мои диалоги", responses=error_docs(401))
async def conversations(request: Request, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0),
                        identity: Identity = Depends(current_identity)):
    items, total = await request.app.state.chat.conversations(identity, limit, offset)
    return ConversationPage(items=items, total=total)


@router.get("/conversations/{conversation_id}", response_model=ConversationFull, summary="Диалог с сообщениями",
            responses=error_docs(401, 404))
async def conversation(conversation_id: str, request: Request, identity: Identity = Depends(current_identity)):
    return await request.app.state.chat.conversation(identity, conversation_id)


@router.delete("/conversations/{conversation_id}", status_code=204, summary="Удалить диалог",
               responses=error_docs(401, 404))
async def delete_conversation(conversation_id: str, request: Request, identity: Identity = Depends(current_identity)):
    await request.app.state.chat.delete(identity, conversation_id)
    return Response(status_code=204)
