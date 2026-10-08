"""Синхронизация корпуса с источником (логика grabber из Lab1, хранилище — своя БД сервиса).

- новые и изменённые документы определяются по git blob SHA; неизменённые не скачиваются;
- содержимое проверяется по SHA (повреждённый или неполный файл не сохраняется);
- документ с уже встреченным SHA в другом пути — дубль, пропускается;
- исчезнувшие из источника документы удаляются;
- ошибка одного файла не останавливает запуск (статус partial, повторный запуск докачает);
- по итогу — события documents.changed для indexing-service (пачками по event_batch_size документов).
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import delete, select, update

from ingestion_service.models import Document, SyncRun
from ingestion_service.source import RemoteFile, Source, document_metadata, git_blob_sha
from rag_common.events import publish_safely

log = logging.getLogger(__name__)

EVENT_DOCUMENTS_CHANGED = "documents.changed"


@dataclass
class Stats:
    added: int = 0
    updated: int = 0
    unchanged: int = 0
    deleted: int = 0
    duplicates: int = 0
    failed: int = 0


class Syncer:
    def __init__(self, source: Source, sessions, bus, *, site_url: str, source_name: str, max_workers: int,
                 fetch_limit: int = 0, event_batch_size: int = 50):
        self.source = source
        self.sessions = sessions
        self.bus = bus
        self.site_url = site_url
        self.source_name = source_name
        self.max_workers = max_workers
        self.fetch_limit = fetch_limit
        self.event_batch_size = event_batch_size

    async def run(self, run_id: str) -> None:
        stats = Stats()
        try:
            commit_sha, changed, deleted = await self._sync(stats)
        except Exception as error:  # noqa: BLE001 — запуск помечается failed, сервис продолжает работать
            log.exception("Синхронизация %s не удалась", run_id)
            await self._finish(run_id, "failed", stats, error=f"{type(error).__name__}: {error}"[:1000])
            return
        status = "partial" if stats.failed else "succeeded"
        await self._finish(run_id, status, stats, commit_sha=commit_sha)
        log.info("Синхронизация %s: %s", run_id, status, extra={"run_id": run_id, **stats.__dict__})
        await self._publish(run_id, commit_sha, changed, deleted)

    async def _publish(self, run_id: str, commit_sha: str, changed: list[str], deleted: list[str]) -> None:
        """documents.changed пачками по event_batch_size изменённых документов; удалённые — в первой пачке."""
        if not changed and not deleted:
            return
        size = self.event_batch_size
        batches = [changed[i:i + size] for i in range(0, len(changed), size)] or [[]]
        for number, batch in enumerate(batches, 1):
            await publish_safely(self.bus, EVENT_DOCUMENTS_CHANGED, {
                "run_id": run_id, "commit_sha": commit_sha, "changed": batch,
                "deleted": deleted if number == 1 else [], "batch": number, "batches": len(batches),
            })

    async def _sync(self, stats: Stats) -> tuple[str, list[str], list[str]]:
        snapshot = await asyncio.to_thread(self.source.snapshot)
        async with self.sessions() as session:
            known = dict((await session.execute(select(Document.id, Document.sha))).all())

        to_fetch, keep = self._plan(snapshot.files, known, stats)
        to_delete = sorted(set(known) - keep)
        if self.fetch_limit:
            to_fetch = to_fetch[: self.fetch_limit]
        log.info("План: скачать %d, удалить %d, без изменений %d, дублей %d",
                 len(to_fetch), len(to_delete), stats.unchanged, stats.duplicates)

        downloaded = await asyncio.to_thread(self._download, to_fetch, snapshot.commit_sha, stats)
        now = datetime.now(UTC)
        async with self.sessions() as session:
            for remote, data, text in downloaded:
                is_update = remote.path in known
                await session.merge(Document(
                    id=remote.path, sha=remote.sha, source=self.source_name, content=text, size=len(data),
                    commit_sha=snapshot.commit_sha, commit_date=snapshot.commit_date, updated_at=now,
                    **document_metadata(remote.path, text, self.site_url),
                ))
                stats.updated += is_update
                stats.added += not is_update
            if to_delete:
                await session.execute(delete(Document).where(Document.id.in_(to_delete)))
                stats.deleted = len(to_delete)
            await session.commit()
        return snapshot.commit_sha, sorted(remote.path for remote, _, _ in downloaded), to_delete

    @staticmethod
    def _plan(files: list[RemoteFile], known: dict[str, str], stats: Stats) -> tuple[list[RemoteFile], set[str]]:
        to_fetch, keep, seen = [], set(), {}
        for remote in sorted(files, key=lambda item: item.path):
            if remote.sha in seen:
                stats.duplicates += 1
                log.info("Дубль содержимого: %s совпадает с %s, пропущен", remote.path, seen[remote.sha])
                continue
            seen[remote.sha] = remote.path
            keep.add(remote.path)
            if known.get(remote.path) == remote.sha:
                stats.unchanged += 1
            else:
                to_fetch.append(remote)
        return to_fetch, keep

    def _download(self, files: list[RemoteFile], commit_sha: str, stats: Stats) -> list[tuple[RemoteFile, bytes, str]]:
        """Параллельная загрузка в потоках (requests — блокирующий клиент)."""
        result = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as pool:
            futures = {pool.submit(self.source.fetch, remote.path, commit_sha): remote for remote in files}
            for future in as_completed(futures):
                remote = futures[future]
                try:
                    data = future.result()
                    if git_blob_sha(data) != remote.sha:
                        raise ValueError("содержимое не совпадает с SHA (файл повреждён или неполный)")
                    result.append((remote, data, data.decode("utf-8")))
                except Exception as error:  # noqa: BLE001 — ошибка одного документа не фатальна
                    stats.failed += 1
                    log.warning("Не удалось получить %s: %s", remote.path, error)
        return result

    async def _finish(self, run_id: str, status: str, stats: Stats, *, commit_sha: str | None = None,
                      error: str | None = None) -> None:
        async with self.sessions() as session:
            await session.execute(update(SyncRun).where(SyncRun.id == run_id).values(
                status=status, finished_at=datetime.now(UTC), commit_sha=commit_sha, error=error, **stats.__dict__,
            ))
            await session.commit()
