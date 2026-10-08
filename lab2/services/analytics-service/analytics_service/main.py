"""analytics-service: качество работы системы по событиям других сервисов и оценки пользователей.

Запуск: uvicorn analytics_service.main:create_app --factory --port 8007
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from analytics_service.api import router
from analytics_service.config import Settings
from analytics_service.projector import ROUTING_KEYS, Projector
from rag_common.app import create_app as create_service_app
from rag_common.db import Base, create_database, init_schema, ping
from rag_common.events import InMemoryEventBus, RabbitEventBus


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    engine, sessions = create_database(settings.database_url)
    await init_schema(engine, Base.metadata)
    app.state.sessions = sessions
    bus = app.state.event_bus
    bus.subscribe(settings.events_queue, ROUTING_KEYS, Projector(sessions).handle)
    await bus.start()
    app.state.ready_checks = {"database": lambda: ping(engine)}
    if isinstance(bus, RabbitEventBus):
        app.state.ready_checks["broker"] = bus.check  # сервис живёт событиями: без брокера данных не будет
    yield
    await bus.close()
    await engine.dispose()


def create_app(settings: Settings | None = None, event_bus=None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="analytics-service",
        description="Аналитика по событиям question.answered, index.updated, user.registered: доля отказов, "
                    "задержки, цитируемые документы, оценки ответов пользователями.",
        routers=[router],
        lifespan=lifespan,
    )
    app.state.event_bus = event_bus or (
        RabbitEventBus(settings.rabbitmq_url, settings.service_name) if settings.rabbitmq_url
        else InMemoryEventBus(settings.service_name)
    )
    return app
