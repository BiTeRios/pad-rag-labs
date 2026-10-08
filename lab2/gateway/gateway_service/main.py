"""API Gateway: единая точка входа. Маршрутизация, JWT, роли, rate limiting, request ID, агрегация статуса.

Запуск: uvicorn gateway_service.main:create_app --factory --port 8000
"""

from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from gateway_service.config import Settings
from gateway_service.proxy import DOCUMENTED_SERVICES, router
from gateway_service.routing import RateLimiter, load_routes
from rag_common.app import create_app as create_service_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http = httpx.AsyncClient(transport=app.state.transport)
    yield
    await app.state.http.aclose()


def create_app(settings: Settings | None = None, transport: httpx.AsyncBaseTransport | None = None) -> FastAPI:
    settings = settings or Settings()
    docs = ", ".join(f"[{name}](/docs/{name})" for name in DOCUMENTED_SERVICES)
    app = create_service_app(
        settings,
        title="RAG API Gateway",
        description="Единая точка входа: маршрутизация к сервисам, проверка JWT и ролей, rate limiting, "
                    f"X-Request-ID. Документация сервисов через gateway: {docs}.",
        routers=[router],
        lifespan=lifespan,
    )
    app.state.service_urls = settings.service_urls()
    app.state.routes = load_routes(settings.routes_file, set(app.state.service_urls))  # ошибка в маршрутах — не стартуем
    app.state.limiter = RateLimiter()
    app.state.transport = transport
    return app
