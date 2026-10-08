"""Сборка FastAPI-приложения сервиса: логи, request ID, ошибки, /health и /ready, Swagger на /docs."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi import APIRouter, FastAPI

from rag_common.errors import install_error_handlers
from rag_common.health import router as health_router
from rag_common.logging import setup_logging
from rag_common.middleware import RequestContextMiddleware


class ServiceSettings(BaseSettings):
    """Общие параметры; у каждого сервиса — наследник со своими. Источник: переменные окружения, затем .env."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    service_name: str
    log_level: str = "INFO"


def create_app(settings: ServiceSettings, *, title: str, description: str, version: str = "1.0.0",
               routers: list[APIRouter], lifespan=None) -> FastAPI:
    setup_logging(settings.service_name, settings.log_level)
    app = FastAPI(title=title, description=description, version=version, lifespan=lifespan)
    app.state.settings = settings
    app.state.ready_checks = {}
    app.add_middleware(RequestContextMiddleware)
    install_error_handlers(app)
    app.include_router(health_router)
    for router in routers:
        app.include_router(router)
    return app
