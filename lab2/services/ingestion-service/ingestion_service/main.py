"""ingestion-service: автоматический сбор документации из GitHub в собственную БД.

Запуск: uvicorn ingestion_service.main:create_app --factory --port 8002
"""

import asyncio
import contextlib
import logging
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import FastAPI
from sqlalchemy import update

from ingestion_service.api import internal, router, start_run
from ingestion_service.config import Settings
from ingestion_service.models import SyncRun
from ingestion_service.source import GitHubSource
from ingestion_service.syncer import Syncer
from rag_common.app import create_app as create_service_app
from rag_common.db import Base, create_database, init_schema, ping
from rag_common.errors import Conflict
from rag_common.events import InMemoryEventBus, RabbitEventBus

log = logging.getLogger(__name__)


async def _schedule(app: FastAPI, minutes: int) -> None:
    while True:
        await asyncio.sleep(minutes * 60)
        with contextlib.suppress(Conflict):  # предыдущий запуск ещё идёт — пропускаем
            await start_run(app, "schedule")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    engine, sessions = create_database(settings.database_url)
    await init_schema(engine, Base.metadata)
    async with sessions() as session:  # запуски, прерванные перезапуском сервиса, не должны висеть в running
        await session.execute(update(SyncRun).where(SyncRun.status == "running").values(
            status="failed", finished_at=datetime.now(UTC), error="прерван перезапуском сервиса"))
        await session.commit()

    bus = app.state.event_bus
    await bus.start()
    source = app.state.source or GitHubSource(
        settings.github_repo, settings.github_ref, settings.docs_root, settings.sections, settings.extensions,
        token=settings.github_token, timeout_s=settings.http_timeout_s, max_retries=settings.max_retries,
        backoff_s=settings.backoff_s, pool_size=settings.max_workers,
    )
    app.state.sessions = sessions
    app.state.syncer = Syncer(source, sessions, bus, site_url=settings.site_url, source_name=settings.source_name,
                              max_workers=settings.max_workers, fetch_limit=settings.fetch_limit,
                              event_batch_size=settings.event_batch_size)
    app.state.sync_busy = False
    # Брокер в готовность не входит: события здесь уведомительные (publish_safely), без брокера сервис работает
    app.state.ready_checks = {"database": lambda: ping(engine)}
    scheduler = asyncio.create_task(_schedule(app, settings.sync_interval_minutes)) if settings.sync_interval_minutes else None
    yield
    for task in (scheduler, getattr(app.state, "sync_task", None)):
        if task and not task.done():
            task.cancel()
    await bus.close()
    await engine.dispose()


def create_app(settings: Settings | None = None, event_bus=None, source=None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="ingestion-service",
        description="Автоматический сбор документации Kubernetes из GitHub: инкрементально по git SHA, "
                    "без дублей, с проверкой целостности. Хранит документы и историю запусков.",
        routers=[router, internal],
        lifespan=lifespan,
    )
    app.state.event_bus = event_bus or (
        RabbitEventBus(settings.rabbitmq_url, settings.service_name) if settings.rabbitmq_url
        else InMemoryEventBus(settings.service_name)
    )
    app.state.source = source
    return app
