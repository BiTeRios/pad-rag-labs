"""Источник документов: GitHub-репозиторий (REST API для списка файлов, raw для содержимого)."""

import logging
from dataclasses import dataclass
from urllib.parse import quote

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://api.github.com"
RAW_URL = "https://raw.githubusercontent.com"

log = logging.getLogger(__name__)


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


class GitHubSource:
    def __init__(
        self,
        repo: str,
        ref: str,
        docs_root: str,
        sections: list[str],
        extensions: list[str],
        token: str | None = None,
        timeout_s: float = 30,
        max_retries: int = 3,
        backoff_s: float = 1.0,
        pool_size: int = 8,
    ):
        self.repo = repo
        self.ref = ref
        self.docs_root = docs_root.strip("/")
        self.sections = sections
        self.extensions = tuple(extensions)
        self.timeout_s = timeout_s

        retry = Retry(
            total=max_retries,
            backoff_factor=backoff_s,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("GET",),
            respect_retry_after_header=True,
        )
        adapter = HTTPAdapter(max_retries=retry, pool_connections=2, pool_maxsize=pool_size)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.headers["Accept"] = "application/vnd.github+json"
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def snapshot(self) -> Snapshot:
        """Список файлов выбранных разделов на текущем коммите ветки (1 + 1 + N запросов к API)."""
        commit = self._get_json(f"{API_URL}/repos/{self.repo}/commits/{self.ref}")
        commit_sha = commit["sha"]
        commit_date = commit["commit"]["committer"]["date"]

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

        log.info("Коммит %s (%s): %d файлов в разделах %s", commit_sha[:10], commit_date, len(files), self.sections)
        return Snapshot(commit_sha, commit_date, files)

    def fetch(self, path: str, commit_sha: str) -> bytes:
        """Содержимое файла на зафиксированном коммите, чтобы оно совпадало с SHA из snapshot()."""
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
            raise SourceError("исчерпан лимит GitHub API (60 запросов/час без токена), задайте GITHUB_TOKEN в .env")
        if response.status_code != 200:
            raise SourceError(f"GitHub API вернул {response.status_code} для {url}: {response.text[:200]}")
        return response.json()
