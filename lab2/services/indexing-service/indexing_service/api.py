import asyncio
import logging

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, Field

from rag_common.auth import Identity, current_identity, require_role
from rag_common.errors import BadRequest, Conflict, error_docs

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/indexing", tags=["indexing"])
internal = APIRouter(prefix="/internal", tags=["internal"])


class StatusResponse(BaseModel):
    collection: str | None
    embedding_model: str | None
    chunking: dict
    points: int | None
    documents: int | None
    running: dict | None = Field(description="текущая задача, если идёт")
    last_job: dict | None


class SearchRequest(BaseModel):
    vector: list[float] = Field(min_length=1)
    limit: int = Field(20, ge=1)
    filters: dict[str, str | list[str]] | None = Field(None, examples=[{"section": "concepts/workloads/pods"}])


class SearchResponse(BaseModel):
    collection: str
    points: list[dict] = Field(description="payload chunk (text, heading, url, …) + score — косинусная близость")


@router.get("/status", response_model=StatusResponse, summary="Состояние индекса", responses=error_docs(401))
async def status(request: Request, _: Identity = Depends(current_identity)):
    indexer, s = request.app.state.indexer, request.app.state.settings
    points = documents = None
    if indexer.store.collection:
        points = await indexer.store.count()
        documents = len(await indexer.store.indexed_documents())
    return StatusResponse(
        collection=indexer.store.collection, embedding_model=indexer.embedding_model,
        chunking={"strategy": s.chunk_strategy, "chunk_size": s.chunk_size, "chunk_overlap": s.chunk_overlap,
                  "include_heading": s.include_heading},
        points=points, documents=documents, running=indexer.current_job, last_job=indexer.last_job,
    )


@router.post("/reconcile", status_code=202, summary="Сверить индекс с корпусом (admin)",
             description="Переиндексирует документы, чьи SHA расходятся с ingestion-service, и удаляет лишние. "
                         "Идёт в фоне; итог — в GET /api/indexing/status.",
             responses=error_docs(401, 403, 409))
async def reconcile(request: Request, _: Identity = Depends(require_role("admin"))):
    indexer = request.app.state.indexer
    if indexer.lock.locked():
        raise Conflict("Индексация уже идёт", code="indexing_running")
    request.app.state.jobs.add(task := asyncio.create_task(request.app.state.run_reconcile("manual")))
    task.add_done_callback(request.app.state.jobs.discard)
    return {"status": "accepted"}


@internal.post("/search", response_model=SearchResponse, summary="Ближайшие chunks к вектору",
               responses=error_docs(400, 422, 503))
async def search(body: SearchRequest, request: Request):
    indexer = request.app.state.indexer
    if body.limit > request.app.state.settings.max_search_limit:
        raise BadRequest(f"limit не больше {request.app.state.settings.max_search_limit}")
    await indexer.prepare()
    points = await indexer.store.search(body.vector, body.limit, body.filters)
    return SearchResponse(collection=indexer.store.collection, points=points)
