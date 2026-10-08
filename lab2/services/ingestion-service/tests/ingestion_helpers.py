import threading
import time

from ingestion_service.source import RemoteFile, Snapshot, git_blob_sha
from rag_common.testing import as_admin


class FakeSource:
    """Источник в памяти: {путь: текст}; можно «сломать» отдельные файлы и задержать скачивание."""

    def __init__(self, files: dict[str, str]):
        self.files = dict(files)
        self.broken: set[str] = set()
        self.gate = threading.Event()
        self.gate.set()
        self.fetched: list[str] = []
        self.commit = 1

    def snapshot(self) -> Snapshot:
        files = [RemoteFile(path, git_blob_sha(text.encode()), len(text)) for path, text in self.files.items()]
        return Snapshot(f"{self.commit:040d}", "2026-10-08T00:00:00Z", files)

    def fetch(self, path: str, commit_sha: str) -> bytes:
        self.gate.wait(5)
        self.fetched.append(path)
        if path in self.broken:
            return b"truncated"  # не совпадёт с SHA
        return self.files[path].encode()


def run_sync(client) -> dict:
    """Запускает синхронизацию и ждёт её окончания."""
    response = client.post("/api/ingestion/runs", headers=as_admin())
    assert response.status_code == 202, response.text
    return wait_run(client, response.json()["id"])


def wait_run(client, run_id: str, timeout_s: float = 5.0) -> dict:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        run = client.get(f"/api/ingestion/runs/{run_id}", headers=as_admin()).json()
        if run["status"] != "running":
            return run
        time.sleep(0.02)
    raise AssertionError("синхронизация не завершилась")
