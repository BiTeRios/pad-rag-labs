"""chat-service: ответы на вопросы по документации (RAG) и история диалогов.

Запуск: uvicorn chat_service.main:create_app --factory --port 8006
"""

from contextlib import asynccontextmanager

import yaml
from fastapi import FastAPI

from chat_service.api import router
from chat_service.config import Settings
from chat_service.generator import AnswerGenerator
from chat_service.llm import OllamaClient
from chat_service.service import ChatService
from rag_common.app import create_app as create_service_app
from rag_common.db import Base, create_database, init_schema, ping
from rag_common.events import InMemoryEventBus, RabbitEventBus
from rag_common.http import ServiceClient


def load_prompt(settings: Settings) -> dict:
    prompts = yaml.safe_load(settings.prompts_file.read_text(encoding="utf-8"))
    if settings.prompt_name not in prompts:
        raise ValueError(f"промпта '{settings.prompt_name}' нет в {settings.prompts_file}: {list(prompts)}")
    return prompts[settings.prompt_name]


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings: Settings = app.state.settings
    prompt = load_prompt(settings)  # ошибка в промпте — сервис не стартует, а не отвечает мусором
    engine, sessions = create_database(settings.database_url)
    await init_schema(engine, Base.metadata)
    retrieval = ServiceClient("retrieval-service", settings.retrieval_url, settings.retrieval_timeout_s,
                              transport=app.state.transports.get("retrieval"))
    llm = OllamaClient(settings.llm_base_url, settings.llm_model, temperature=settings.llm_temperature,
                       num_ctx=settings.llm_num_ctx, think=settings.llm_think, seed=settings.llm_seed,
                       timeout_s=settings.llm_timeout_s, transport=app.state.transports.get("llm"))
    generator = AnswerGenerator(llm, prompt["system"].format(no_context_answer=settings.no_context_answer),
                                prompt["user"], settings.no_context_answer, settings.refusal_marker)
    bus = app.state.event_bus
    await bus.start()
    app.state.chat = ChatService(sessions, retrieval, generator, bus, settings)
    # Готовность — только своя БД: без LLM и поиска история диалогов всё равно доступна,
    # а их сбой на /ask даёт понятную ошибку 502/504.
    app.state.ready_checks = {"database": lambda: ping(engine)}
    yield
    await bus.close()
    await retrieval.close()
    await llm.close()
    await engine.dispose()


def create_app(settings: Settings | None = None, event_bus=None, transports: dict | None = None) -> FastAPI:
    settings = settings or Settings()
    app = create_service_app(
        settings,
        title="chat-service",
        description="Ответы на вопросы по документации Kubernetes: поиск контекста, генерация ответа LLM "
                    "со ссылками на источники, отказ при нехватке информации, история диалогов.",
        routers=[router],
        lifespan=lifespan,
    )
    app.state.event_bus = event_bus or (
        RabbitEventBus(settings.rabbitmq_url, settings.service_name) if settings.rabbitmq_url
        else InMemoryEventBus(settings.service_name)
    )
    app.state.transports = transports or {}
    return app
