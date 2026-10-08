from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from rag_common.auth import Identity, current_identity
from rag_common.errors import BadRequest, error_docs

router = APIRouter(prefix="/api", tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, examples=["Как ограничить потребление памяти контейнером?"])
    top_k: int | None = Field(None, ge=1, description="по умолчанию TOP_K из конфигурации")
    section: str | None = Field(None, examples=["concepts/workloads/pods"], description="искать только в разделе")


class Chunk(BaseModel):
    chunk_id: str
    document_id: str
    title: str
    heading: str
    url: str
    section: str
    text: str
    score: float = Field(description="косинусная близость векторного поиска")
    rerank_score: float | None = Field(None, description="релевантность по cross-encoder, 0..1")


class SearchResponse(BaseModel):
    query: str
    chunks: list[Chunk] = Field(description="пусто — в базе нет достаточно релевантного контекста")
    stages: dict[str, int] = Field(description="сколько chunks осталось после каждого шага")
    timings_ms: dict[str, float]
    degraded: list[str] = Field(description="шаги, пропущенные из-за сбоя соседнего сервиса")


@router.post("/search", response_model=SearchResponse, summary="Семантический поиск по документации",
             responses=error_docs(400, 401, 422, 502, 504))
async def search(body: SearchRequest, request: Request, _: Identity = Depends(current_identity)):
    settings = request.app.state.settings
    query = body.query.strip()
    if not query or len(query) > settings.max_query_chars:
        raise BadRequest(f"Запрос должен быть от 1 до {settings.max_query_chars} символов", code="invalid_query")
    if body.top_k and body.top_k > settings.max_top_k:
        raise BadRequest(f"top_k не больше {settings.max_top_k}", code="invalid_top_k")
    result = await request.app.state.pipeline.run(query, body.top_k, {"section": body.section} if body.section else None)
    return SearchResponse(query=query, chunks=result.chunks, stages=result.stages, timings_ms=result.timings_ms,
                          degraded=result.degraded)
