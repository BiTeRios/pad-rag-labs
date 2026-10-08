"""retrieval-service: поиск контекста — фильтры, пороги, reranker. Своих данных не хранит.

Запуск: uvicorn retrieval_service.main:create_app --factory --port 8005
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from retrieval_service.api import router
from retrieval_service.config import Settings
from retrieval_service.pipeline import RetrievalPipeline
from rag_common.app import create_app as create_service_app
from rag_common.http import ServiceClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    inference = ServiceClient("inference-service", settings.inference_url, settings.inference_timeout_s,
                              transport=app.state.transports.get("inference"))
    indexing = ServiceClient("indexing-service", settings.indexing_url, settings.indexing_timeout_s,
                             transport=app.state.transports.get("indexing"))
    app.state.pipeline = RetrievalPipeline(inference, indexing, settings)
    app.state.ready_checks = {"inference": inference.check, "indexing": indexing.check}
    yield
    await inference.close()
    await indexing.close()


def create_app(settings: Settings | None = None, transports: dict | None = None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="retrieval-service",
        description="Поиск контекста для вопроса: векторный поиск (indexing-service), порог близости, "
                    "удаление почти-дублей и коротких chunks, cross-encoder reranker (inference-service), top-K.",
        routers=[router],
        lifespan=lifespan,
    )
    app.state.transports = transports or {}
    return app
