"""auth-service: пользователи, пароли, роли и выпуск JWT.

Запуск: uvicorn auth_service.main:create_app --factory --port 8001
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth_service.api import router
from auth_service.config import Settings
from auth_service.service import UserService
from rag_common.app import create_app as create_service_app
from rag_common.db import Base, create_database, init_schema, ping
from rag_common.events import InMemoryEventBus, RabbitEventBus


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    engine, sessions = create_database(settings.database_url)
    await init_schema(engine, Base.metadata)
    app.state.sessions = sessions
    if settings.admin_email and settings.admin_password:
        async with sessions() as session:
            await UserService(session, settings.password_min_length).ensure_admin(settings.admin_email, settings.admin_password)

    bus = app.state.event_bus
    await bus.start()
    # Брокер в готовность не входит: события здесь уведомительные (publish_safely), без брокера сервис работает
    app.state.ready_checks = {"database": lambda: ping(engine)}
    yield
    await bus.close()
    await engine.dispose()


def create_app(settings: Settings | None = None, event_bus=None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="auth-service",
        description="Регистрация, вход и роли пользователей; выпуск JWT для gateway.",
        routers=[router],
        lifespan=lifespan,
    )
    if event_bus is None:
        event_bus = RabbitEventBus(settings.rabbitmq_url, settings.service_name) if settings.rabbitmq_url \
            else InMemoryEventBus(settings.service_name)
    app.state.event_bus = event_bus
    return app
