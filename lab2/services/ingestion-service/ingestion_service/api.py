import asyncio
import logging

from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy import func, or_, select

from ingestion_service.models import Document, SyncRun
from ingestion_service.schemas import BatchRequest, DocumentFull, DocumentPage, Fingerprint, RunOut
from rag_common.auth import Identity, current_identity, require_role
from rag_common.errors import Conflict, NotFound, error_docs

log = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ingestion", tags=["ingestion"])
internal = APIRouter(prefix="/internal", tags=["internal"])  # только для сервисов, gateway не проксирует


async def start_run(app, trigger: str) -> SyncRun:
    """Один запуск за раз: флаг ставится до первого await, поэтому два запроса не стартуют два запуска."""
    if app.state.sync_busy:
        raise Conflict("Синхронизация уже идёт", code="sync_running")
    app.state.sync_busy = True
    try:
        async with app.state.sessions() as session:
            run = SyncRun(trigger=trigger)
            session.add(run)
            await session.commit()
    except Exception:
        app.state.sync_busy = False
        raise

    async def execute() -> None:
        try:
            await app.state.syncer.run(run.id)
        finally:
            app.state.sync_busy = False

    app.state.sync_task = asyncio.create_task(execute(), name=f"sync-{run.id}")
    log.info("Синхронизация запущена", extra={"run_id": run.id, "trigger": trigger})
    return run


@router.post("/runs", status_code=202, response_model=RunOut, summary="Запустить синхронизацию (admin)",
             description="Запуск идёт в фоне; статус — GET /api/ingestion/runs/{id}. По итогу публикуется documents.changed.",
             responses=error_docs(401, 403, 409))
async def create_run(request: Request, _: Identity = Depends(require_role("admin"))):
    return await start_run(request.app, "manual")


@router.get("/runs", response_model=list[RunOut], summary="Последние запуски (admin)", responses=error_docs(401, 403))
async def list_runs(request: Request, limit: int = Query(20, ge=1, le=100), _: Identity = Depends(require_role("admin"))):
    async with request.app.state.sessions() as session:
        return list(await session.scalars(select(SyncRun).order_by(SyncRun.started_at.desc()).limit(limit)))


@router.get("/runs/{run_id}", response_model=RunOut, summary="Статус запуска (admin)", responses=error_docs(401, 403, 404))
async def get_run(run_id: str, request: Request, _: Identity = Depends(require_role("admin"))):
    async with request.app.state.sessions() as session:
        run = await session.get(SyncRun, run_id)
    if run is None:
        raise NotFound("Запуск не найден")
    return run


@router.get("/documents", response_model=DocumentPage, summary="Документы корпуса", responses=error_docs(401))
async def list_documents(
    request: Request,
    section: str | None = Query(None, description="префикс раздела, например concepts/workloads"),
    q: str | None = Query(None, min_length=2, description="подстрока в заголовке"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    _: Identity = Depends(current_identity),
):
    query = select(Document)
    if section:
        query = query.where(or_(Document.section == section, Document.section.startswith(f"{section}/")))
    if q:
        query = query.where(Document.title.ilike(f"%{q}%"))
    async with request.app.state.sessions() as session:
        total = await session.scalar(select(func.count()).select_from(query.subquery()))
        items = await session.scalars(query.order_by(Document.id).limit(limit).offset(offset))
        return DocumentPage(items=list(items), total=total)


@router.get("/documents/{doc_id:path}", response_model=DocumentFull, summary="Документ с исходным текстом",
            responses=error_docs(401, 404))
async def get_document(doc_id: str, request: Request, _: Identity = Depends(current_identity)):
    return await _document(request, doc_id)


@internal.get("/documents", response_model=list[Fingerprint], summary="id и SHA всех документов (для сверки индекса)")
async def fingerprints(request: Request):
    async with request.app.state.sessions() as session:
        rows = await session.execute(select(Document.id, Document.sha).order_by(Document.id))
        return [Fingerprint(id=row.id, sha=row.sha) for row in rows]


@internal.post("/documents/batch", response_model=list[DocumentFull], summary="Документы по списку id (для индексации)",
               description="Отсутствующие id пропускаются: документ мог быть удалён после события.")
async def documents_batch(body: BatchRequest, request: Request):
    async with request.app.state.sessions() as session:
        return list(await session.scalars(select(Document).where(Document.id.in_(body.ids)).order_by(Document.id)))


@internal.get("/documents/{doc_id:path}", response_model=DocumentFull, responses=error_docs(404))
async def internal_document(doc_id: str, request: Request):
    return await _document(request, doc_id)


async def _document(request: Request, doc_id: str) -> Document:
    async with request.app.state.sessions() as session:
        document = await session.get(Document, doc_id)
    if document is None:
        raise NotFound(f"Документ {doc_id} не найден")
    return document
