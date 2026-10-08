"""inference-service: модели эмбеддингов и reranker — одна копия весов для индексации и поиска.

Запуск: uvicorn inference_service.main:create_app --factory --port 8003
Модели грузятся в фоне после старта: /health отвечает сразу, /ready — когда модели в памяти.
"""

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from inference_service.api import router
from inference_service.config import Settings
from inference_service.models import Models
from rag_common.app import create_app as create_service_app


async def _models_loaded(models: Models) -> None:
    if not models.loaded:
        raise RuntimeError(models.error or "модели загружаются")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    models = app.state.models
    app.state.limiter = asyncio.Semaphore(settings.max_concurrency)
    app.state.ready_checks = {"models": lambda: _models_loaded(models)}
    loader = None if models.loaded else asyncio.create_task(asyncio.to_thread(models.load))
    yield
    if loader and not loader.done():
        loader.cancel()


def create_app(settings: Settings | None = None, models=None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="inference-service",
        description="Векторизация текстов (multilingual-e5-base) и cross-encoder reranker (bge-reranker-v2-m3). "
                    "Внутренний сервис: вызывается indexing-service и retrieval-service.",
        routers=[router],
        lifespan=lifespan,
    )
    app.state.models = models or Models(settings)
    return app
