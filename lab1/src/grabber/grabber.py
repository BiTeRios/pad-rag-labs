"""Синхронизация локального корпуса с источником.

Повторный запуск скачивает только новые и изменённые документы (git blob SHA сравнивается
с manifest), удаляет исчезнувшие из источника и не сохраняет дубли по содержимому.
"""

import hashlib
import json
import logging
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Protocol

from src.grabber.github_source import RemoteFile, Snapshot
from src.grabber.metadata import build_metadata

log = logging.getLogger(__name__)


class Source(Protocol):
    def snapshot(self) -> Snapshot: ...

    def fetch(self, path: str, commit_sha: str) -> bytes: ...


@dataclass
class SyncStats:
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    duplicates: int = 0
    failed: int = 0
    failed_paths: list[str] = field(default_factory=list)


def git_blob_sha(data: bytes) -> str:
    """SHA-1 в формате git blob, совпадает с SHA из GitHub git trees API."""
    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


class Grabber:
    def __init__(
        self,
        source: Source,
        raw_dir: Path,
        manifest_path: Path,
        site_url: str,
        source_name: str,
        max_workers: int = 8,
    ):
        self.source = source
        self.raw_dir = raw_dir
        self.manifest_path = manifest_path
        self.site_url = site_url
        self.source_name = source_name
        self.max_workers = max_workers

    def sync(self, dry_run: bool = False, limit: int | None = None) -> SyncStats:
        started_at = _now()
        snapshot = self.source.snapshot()
        manifest = self._load_manifest()
        documents = manifest["documents"]
        stats = SyncStats()

        to_fetch, keep = self._plan(snapshot.files, documents, stats)
        to_delete = sorted(set(documents) - keep)
        if limit is not None:
            to_fetch = to_fetch[:limit]
        log.info(
            "План: скачать %d, удалить %d, без изменений %d, дублей %d",
            len(to_fetch), len(to_delete), stats.unchanged, stats.duplicates,
        )

        if dry_run:
            for remote in to_fetch:
                log.info("  %s %s", "обновить" if remote.path in documents else "добавить", remote.path)
                stats.updated += remote.path in documents
                stats.added += remote.path not in documents
            for path in to_delete:
                log.info("  удалить %s", path)
            stats.deleted = len(to_delete)
            return stats

        for remote, data, text in self._download(to_fetch, snapshot.commit_sha, stats):
            _write_atomic(self.raw_dir / remote.path, data)
            is_update = remote.path in documents
            documents[remote.path] = build_metadata(
                remote.path,
                text,
                sha=remote.sha,
                size=len(data),
                site_url=self.site_url,
                source_name=self.source_name,
                commit_sha=snapshot.commit_sha,
                commit_date=snapshot.commit_date,
                updated_at=_now(),
            )
            stats.updated += is_update
            stats.added += not is_update
            log.debug("%s %s", "Обновлён" if is_update else "Добавлен", remote.path)

        for path in to_delete:
            (self.raw_dir / path).unlink(missing_ok=True)
            del documents[path]
            stats.deleted += 1
            log.info("Удалён (нет в источнике): %s", path)

        manifest["last_sync"] = {
            "started_at": started_at,
            "finished_at": _now(),
            "commit_sha": snapshot.commit_sha,
            "commit_date": snapshot.commit_date,
            "stats": asdict(stats),
        }
        self._save_manifest(manifest)
        return stats

    def _plan(self, files: list[RemoteFile], documents: dict, stats: SyncStats) -> tuple[list[RemoteFile], set[str]]:
        """Что скачать и какие документы оставить. Файл с уже встреченным SHA считается дублем."""
        to_fetch, keep, seen = [], set(), {}
        for remote in sorted(files, key=lambda item: item.path):
            if remote.sha in seen:
                stats.duplicates += 1
                log.info("Дубль содержимого: %s совпадает с %s, пропущен", remote.path, seen[remote.sha])
                continue
            seen[remote.sha] = remote.path
            keep.add(remote.path)
            known = documents.get(remote.path)
            if known and known["sha"] == remote.sha and (self.raw_dir / remote.path).is_file():
                stats.unchanged += 1
            else:
                to_fetch.append(remote)
        return to_fetch, keep

    def _download(
        self, files: list[RemoteFile], commit_sha: str, stats: SyncStats
    ) -> Iterator[tuple[RemoteFile, bytes, str]]:
        """Параллельная загрузка. Ошибка одного файла логируется и не останавливает остальные."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self.source.fetch, remote.path, commit_sha): remote for remote in files}
            for future in as_completed(futures):
                remote = futures[future]
                try:
                    data = future.result()
                    if git_blob_sha(data) != remote.sha:
                        raise ValueError("содержимое не совпадает с SHA (файл повреждён или неполный)")
                    text = data.decode("utf-8")
                except Exception as error:  # noqa: BLE001 — любая ошибка документа не фатальна
                    stats.failed += 1
                    stats.failed_paths.append(remote.path)
                    log.warning("Не удалось получить %s: %s", remote.path, error)
                    continue
                yield remote, data, text

    def _load_manifest(self) -> dict:
        if not self.manifest_path.is_file():
            return {"documents": {}}
        with self.manifest_path.open(encoding="utf-8") as file:
            manifest = json.load(file)
        manifest.setdefault("documents", {})
        return manifest

    def _save_manifest(self, manifest: dict) -> None:
        payload = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True)
        _write_atomic(self.manifest_path, payload.encode("utf-8"))


def _write_atomic(path: Path, data: bytes) -> None:
    """Запись через временный файл: прерванный запуск не оставит полузаписанный документ."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
