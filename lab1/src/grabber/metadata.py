"""Metadata документа: front matter Hugo, ссылка на страницу сайта, заголовок."""

import logging
import re
from pathlib import PurePosixPath

import yaml

log = logging.getLogger(__name__)

_FRONT_MATTER = re.compile(r"\A﻿?---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)
_HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


def split_front_matter(text: str) -> tuple[dict, str]:
    """Отделяет YAML front matter от тела документа. Некорректный front matter даёт {}."""
    text = text.replace("\r\n", "\n")
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        log.warning("Некорректный front matter: %s", error)
        front = {}
    if not isinstance(front, dict):
        front = {}
    return front, text[match.end():]


def page_url(site_url: str, path: str) -> str:
    """concepts/workloads/pods/_index.md -> {site_url}/concepts/workloads/pods/"""
    pure = PurePosixPath(path)
    page = pure.parent if pure.name == "_index.md" else pure.with_suffix("")
    page_path = "" if str(page) == "." else f"{page.as_posix()}/"
    return f"{site_url.rstrip('/')}/{page_path}"


def build_metadata(
    path: str,
    text: str,
    *,
    sha: str,
    size: int,
    site_url: str,
    source_name: str,
    commit_sha: str,
    commit_date: str,
    updated_at: str,
) -> dict:
    front, body = split_front_matter(text)
    pure = PurePosixPath(path)
    heading = _HEADING.search(body)
    fallback = pure.parent.name if pure.stem == "_index" else pure.stem
    title = front.get("title") or (heading.group(1) if heading else fallback)
    return {
        "document_id": path,  # стабильный идентификатор: путь внутри docs_root
        "source": source_name,
        "url": page_url(site_url, path),
        "title": str(title).strip(),
        "section": str(pure.parent),  # раздел сайта, например concepts/workloads/pods
        "description": " ".join(str(front.get("description") or "").split()),
        "content_type": front.get("content_type"),
        "sha": sha,
        "size": size,
        "commit_sha": commit_sha,
        "commit_date": commit_date,  # дата коммита, на котором снят snapshot
        "updated_at": updated_at,  # когда grabber получил эту версию документа
    }
