from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: str = Field(description="running | succeeded | partial | failed")
    trigger: str
    started_at: datetime
    finished_at: datetime | None
    commit_sha: str | None
    added: int
    updated: int
    unchanged: int
    deleted: int
    duplicates: int
    failed: int
    error: str | None


class DocumentMeta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(examples=["concepts/workloads/pods/_index.md"])
    sha: str
    source: str
    url: str
    title: str
    section: str
    description: str
    size: int
    commit_sha: str
    updated_at: datetime


class DocumentFull(DocumentMeta):
    content: str = Field(description="исходный Markdown")


class DocumentPage(BaseModel):
    items: list[DocumentMeta]
    total: int


class Fingerprint(BaseModel):
    id: str
    sha: str


class BatchRequest(BaseModel):
    ids: list[str] = Field(min_length=1, max_length=100)
