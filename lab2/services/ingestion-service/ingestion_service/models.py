import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from rag_common.db import Base


def _now() -> datetime:
    return datetime.now(UTC)


class Document(Base):
    """Документ корпуса: исходный Markdown и metadata. Идентификатор — путь внутри docs_root."""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(300), primary_key=True)
    sha: Mapped[str] = mapped_column(String(40), index=True)  # git blob SHA
    source: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(500))
    title: Mapped[str] = mapped_column(String(300))
    section: Mapped[str] = mapped_column(String(300), index=True)
    description: Mapped[str] = mapped_column(Text, default="")
    content: Mapped[str] = mapped_column(Text)
    size: Mapped[int] = mapped_column(Integer)
    commit_sha: Mapped[str] = mapped_column(String(40))
    commit_date: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)  # когда получена эта версия


class SyncRun(Base):
    """Запуск синхронизации с источником: статус и статистика."""

    __tablename__ = "sync_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status: Mapped[str] = mapped_column(String(16), default="running")  # running | succeeded | partial | failed
    trigger: Mapped[str] = mapped_column(String(16), default="manual")  # manual | schedule
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    commit_sha: Mapped[str | None] = mapped_column(String(40), nullable=True)
    added: Mapped[int] = mapped_column(Integer, default=0)
    updated: Mapped[int] = mapped_column(Integer, default=0)
    unchanged: Mapped[int] = mapped_column(Integer, default=0)
    deleted: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    failed: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
