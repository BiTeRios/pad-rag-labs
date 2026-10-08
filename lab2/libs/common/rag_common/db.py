"""PostgreSQL через SQLAlchemy (async). Схема создаётся при старте; при недоступной БД — повторы."""

import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

log = logging.getLogger("rag_common.db")


class Base(DeclarativeBase):
    pass


def create_database(url: str) -> tuple[AsyncEngine, async_sessionmaker[AsyncSession]]:
    options = {} if url.startswith("sqlite") else {"pool_pre_ping": True, "pool_size": 5, "max_overflow": 5}
    engine = create_async_engine(url, **options)
    return engine, async_sessionmaker(engine, expire_on_commit=False)


async def init_schema(engine: AsyncEngine, metadata, *, attempts: int = 10, delay_s: float = 2.0) -> None:
    """create_all с повторами: в Compose и Kubernetes БД может подняться позже сервиса."""
    for attempt in range(1, attempts + 1):
        try:
            async with engine.begin() as connection:
                await connection.run_sync(metadata.create_all)
            return
        except Exception as error:  # noqa: BLE001
            if attempt == attempts:
                raise
            log.warning("БД недоступна (%s), попытка %d/%d", type(error).__name__, attempt, attempts)
            await asyncio.sleep(delay_s)


async def ping(engine: AsyncEngine) -> None:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
