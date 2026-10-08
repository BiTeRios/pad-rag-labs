"""Источник документов: GitHub-репозиторий (REST API — список файлов и SHA, raw — содержимое).

Перенесено из Lab1 (src/grabber/github_source.py, metadata.py) без изменений логики.
"""

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import PurePosixPath
from typing import Protocol
from urllib.parse import quote

import requests
import yaml
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://api.github.com"
RAW_URL = "https://raw.githubusercontent.com"

log = logging.getLogger(__name__)

_FRONT_MATTER = re.compile(r"\A﻿?---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)
_HEADING = re.compile(r"^#\s+(.+?)\s*$", re.MULTILINE)


class SourceError(Exception):
    """Список файлов получить нельзя, синхронизация невозможна."""


@dataclass(frozen=True)
class RemoteFile:
    path: str  # относительно docs_root, например concepts/workloads/pods/_index.md
    sha: str  # git blob SHA: меняется при любом изменении содержимого
    size: int


@dataclass(frozen=True)
class Snapshot:
    commit_sha: str
    commit_date: str
    files: list[RemoteFile]


class Source(Protocol):
    def snapshot(self) -> Snapshot: ...

    def fetch(self, path: str, commit_sha: str) -> bytes: ...


class GitHubSource:
    def __init__(self, repo: str, ref: str, docs_root: str, sections: list[str], extensions: list[str], *,
                 token: str | None, timeout_s: float, max_retries: int, backoff_s: float, pool_size: int):
        self.repo = repo
        self.ref = ref
        self.docs_root = docs_root.strip("/")
        self.sections = sections
        self.extensions = tuple(extensions)
        self.timeout_s = timeout_s
        retry = Retry(total=max_retries, backoff_factor=backoff_s, status_forcelist=(429, 500, 502, 503, 504),
                      allowed_methods=("GET",), respect_retry_after_header=True)
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retry, pool_connections=2, pool_maxsize=pool_size))
        self.session.headers["Accept"] = "application/vnd.github+json"
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def snapshot(self) -> Snapshot:
        """Файлы выбранных разделов на текущем коммите ветки (1 + 1 + N запросов к API)."""
        commit = self._get_json(f"{API_URL}/repos/{self.repo}/commits/{self.ref}")
        commit_sha, commit_date = commit["sha"], commit["commit"]["committer"]["date"]
        listing = self._get_json(f"{API_URL}/repos/{self.repo}/contents/{self.docs_root}?ref={commit_sha}")
        dirs = {item["name"]: item["sha"] for item in listing if item["type"] == "dir"}
        files = []
        for section in self.sections:
            if section not in dirs:
                raise SourceError(f"раздел '{section}' не найден в {self.docs_root}")
            tree = self._get_json(f"{API_URL}/repos/{self.repo}/git/trees/{dirs[section]}?recursive=1")
            if tree.get("truncated"):
                raise SourceError(f"GitHub API вернул неполный список файлов раздела '{section}'")
            for item in tree["tree"]:
                path = f"{section}/{item['path']}"
                if item["type"] == "blob" and path.endswith(self.extensions):
                    files.append(RemoteFile(path, item["sha"], item.get("size", 0)))
        log.info("Коммит %s: %d файлов в разделах %s", commit_sha[:10], len(files), self.sections)
        return Snapshot(commit_sha, commit_date, files)

    def fetch(self, path: str, commit_sha: str) -> bytes:
        """Содержимое на зафиксированном коммите, чтобы оно совпадало с SHA из snapshot()."""
        url = f"{RAW_URL}/{self.repo}/{commit_sha}/{quote(f'{self.docs_root}/{path}')}"
        response = self.session.get(url, timeout=self.timeout_s)
        response.raise_for_status()
        return response.content

    def _get_json(self, url: str):
        try:
            response = self.session.get(url, timeout=self.timeout_s)
        except requests.RequestException as error:
            raise SourceError(f"GitHub API недоступен: {error}") from error
        if response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
            raise SourceError("исчерпан лимит GitHub API (60 запросов/час без токена), задайте GITHUB_TOKEN")
        if response.status_code != 200:
            raise SourceError(f"GitHub API вернул {response.status_code} для {url}")
        return response.json()


def git_blob_sha(data: bytes) -> str:
    """SHA-1 в формате git blob, совпадает с SHA из GitHub git trees API."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def split_front_matter(text: str) -> tuple[dict, str]:
    text = text.replace("\r\n", "\n")
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        log.warning("Некорректный front matter: %s", error)
        front = {}
    return (front if isinstance(front, dict) else {}), text[match.end():]


def page_url(site_url: str, path: str) -> str:
    """concepts/workloads/pods/_index.md -> {site_url}/concepts/workloads/pods/"""
    pure = PurePosixPath(path)
    page = pure.parent if pure.name == "_index.md" else pure.with_suffix("")
    page_path = "" if str(page) == "." else f"{page.as_posix()}/"
    return f"{site_url.rstrip('/')}/{page_path}"


def document_metadata(path: str, text: str, site_url: str) -> dict:
    front, body = split_front_matter(text)
    pure = PurePosixPath(path)
    heading = _HEADING.search(body)
    fallback = pure.parent.name if pure.stem == "_index" else pure.stem
    return {
        "url": page_url(site_url, path),
        "title": str(front.get("title") or (heading.group(1) if heading else fallback)).strip(),
        "section": str(pure.parent),
        "description": " ".join(str(front.get("description") or "").split()),
    }
