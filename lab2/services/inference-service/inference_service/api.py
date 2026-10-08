import asyncio
import time
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from rag_common.errors import BadRequest, Conflict, ServiceUnavailable, error_docs

router = APIRouter(prefix="/internal", tags=["inference"])


class EmbedRequest(BaseModel):
    texts: list[str] = Field(min_length=1)
    kind: Literal["query", "passage"] = Field(description="query — вопрос, passage — фрагмент документа (разные префиксы e5)")


class EmbedResponse(BaseModel):
    model: str
    dim: int
    vectors: list[list[float]]
    duration_ms: float


class RerankRequest(BaseModel):
    query: str = Field(min_length=1)
    documents: list[str] = Field(min_length=1)


class RerankResponse(BaseModel):
    model: str
    scores: list[float] = Field(description="релевантность 0..1 в порядке documents")
    duration_ms: float


class InfoResponse(BaseModel):
    embedding_model: str
    dim: int | None
    reranker_enabled: bool
    reranker_model: str | None
    device: str | None
    loaded: bool
    error: str | None


@router.post("/embed", response_model=EmbedResponse, summary="Векторы текстов (нормализованы)",
             responses=error_docs(400, 422, 503))
async def embed(body: EmbedRequest, request: Request):
    models, settings = _ready(request)
    _check_limits(body.texts, settings)
    started = time.perf_counter()
    async with request.app.state.limiter:
        vectors = await asyncio.to_thread(models.embed, body.texts, body.kind)
    return EmbedResponse(model=settings.embedding_model, dim=models.dim, vectors=vectors,
                         duration_ms=round((time.perf_counter() - started) * 1000, 1))


@router.post("/rerank", response_model=RerankResponse, summary="Оценка релевантности пар (вопрос, текст)",
             responses=error_docs(400, 409, 422, 503))
async def rerank(body: RerankRequest, request: Request):
    models, settings = _ready(request)
    if not settings.reranker_enabled:
        raise Conflict("Reranker выключен в конфигурации (RERANKER_ENABLED=false)", code="reranker_disabled")
    _check_limits(body.documents, settings)
    started = time.perf_counter()
    async with request.app.state.limiter:
        scores = await asyncio.to_thread(models.rerank, body.query, body.documents)
    return RerankResponse(model=settings.reranker_model, scores=scores,
                          duration_ms=round((time.perf_counter() - started) * 1000, 1))


@router.get("/info", response_model=InfoResponse, summary="Модели, размерность, устройство")
async def info(request: Request):
    models, settings = request.app.state.models, request.app.state.settings
    return InfoResponse(
        embedding_model=settings.embedding_model, dim=models.dim, reranker_enabled=settings.reranker_enabled,
        reranker_model=settings.reranker_model if settings.reranker_enabled else None,
        device=models.device, loaded=models.loaded, error=models.error,
    )


def _ready(request: Request):
    models = request.app.state.models
    if not models.loaded:
        raise ServiceUnavailable("Модели ещё загружаются" if models.error is None else f"Модели не загрузились: {models.error}")
    return models, request.app.state.settings


def _check_limits(texts: list[str], settings) -> None:
    if len(texts) > settings.max_texts:
        raise BadRequest(f"Не больше {settings.max_texts} текстов за запрос", code="too_many_texts")
    if any(len(text) > settings.max_text_chars for text in texts):
        raise BadRequest(f"Текст длиннее {settings.max_text_chars} символов", code="text_too_long")
