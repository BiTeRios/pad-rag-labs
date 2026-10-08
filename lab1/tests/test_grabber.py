import json

import pytest

from src.grabber.github_source import RemoteFile, Snapshot
from src.grabber.grabber import Grabber, git_blob_sha
from src.grabber.metadata import page_url, split_front_matter

SITE = "https://kubernetes.io/docs"

POD = b"---\ntitle: Pods\ncontent_type: concept\ndescription: >\n  Smallest\n  unit.\n---\n\nPods are...\n"
SERVICE = b"---\ntitle: Service\n---\n\nA Service exposes...\n"


class FakeSource:
    """Источник в памяти: files — {path: bytes}; corrupt — что вернуть вместо реального содержимого."""

    def __init__(self, files: dict[str, bytes], fail=(), corrupt=None):
        self.files = dict(files)
        self.fail = set(fail)
        self.corrupt = corrupt or {}
        self.fetched: list[str] = []

    def snapshot(self) -> Snapshot:
        remote = [RemoteFile(path, git_blob_sha(data), len(data)) for path, data in self.files.items()]
        return Snapshot("abc123", "2026-10-07T00:00:00Z", remote)

    def fetch(self, path: str, commit_sha: str) -> bytes:
        self.fetched.append(path)
        if path in self.fail:
            raise ConnectionError("timeout")
        return self.corrupt.get(path, self.files[path])


@pytest.fixture
def make_grabber(tmp_path):
    def make(source):
        return Grabber(source, tmp_path / "raw", tmp_path / "manifest.json", SITE, "kubernetes-docs", max_workers=2)

    return make


def read_manifest(tmp_path) -> dict:
    return json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))["documents"]


def test_first_sync_saves_documents_and_metadata(make_grabber, tmp_path):
    source = FakeSource({"concepts/workloads/pods/_index.md": POD, "concepts/services/service.md": SERVICE})

    stats = make_grabber(source).sync()

    assert (stats.added, stats.failed) == (2, 0)
    assert (tmp_path / "raw/concepts/workloads/pods/_index.md").read_bytes() == POD
    meta = read_manifest(tmp_path)["concepts/workloads/pods/_index.md"]
    assert meta["document_id"] == "concepts/workloads/pods/_index.md"
    assert meta["url"] == "https://kubernetes.io/docs/concepts/workloads/pods/"
    assert meta["title"] == "Pods"
    assert meta["section"] == "concepts/workloads/pods"
    assert meta["description"] == "Smallest unit."
    assert meta["source"] == "kubernetes-docs"
    assert meta["sha"] == git_blob_sha(POD)
    assert meta["updated_at"] and meta["commit_sha"] == "abc123"


def test_second_sync_downloads_nothing_and_creates_no_duplicates(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD, "b.md": SERVICE})
    make_grabber(source).sync()
    source.fetched.clear()

    stats = make_grabber(source).sync()

    assert source.fetched == []
    assert (stats.added, stats.updated, stats.unchanged) == (0, 0, 2)
    assert len(read_manifest(tmp_path)) == 2
    assert len(list((tmp_path / "raw").rglob("*.md"))) == 2


def test_changed_document_is_redownloaded(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD, "b.md": SERVICE})
    make_grabber(source).sync()
    source.files["a.md"] = POD + b"New paragraph.\n"
    source.fetched.clear()

    stats = make_grabber(source).sync()

    assert source.fetched == ["a.md"]
    assert (stats.updated, stats.unchanged) == (1, 1)
    assert (tmp_path / "raw/a.md").read_bytes().endswith(b"New paragraph.\n")
    assert read_manifest(tmp_path)["a.md"]["sha"] == git_blob_sha(source.files["a.md"])


def test_document_removed_from_source_is_deleted(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD, "b.md": SERVICE})
    make_grabber(source).sync()
    del source.files["b.md"]

    stats = make_grabber(source).sync()

    assert stats.deleted == 1
    assert not (tmp_path / "raw/b.md").exists()
    assert set(read_manifest(tmp_path)) == {"a.md"}


def test_failed_download_does_not_stop_others_and_is_retried(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD, "b.md": SERVICE}, fail={"b.md"})

    stats = make_grabber(source).sync()

    assert (stats.added, stats.failed, stats.failed_paths) == (1, 1, ["b.md"])
    assert set(read_manifest(tmp_path)) == {"a.md"}

    source.fail.clear()
    stats = make_grabber(source).sync()
    assert (stats.added, stats.unchanged) == (1, 1)


def test_failed_update_keeps_previous_version(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD})
    make_grabber(source).sync()
    source.files["a.md"] = SERVICE
    source.fail.add("a.md")

    stats = make_grabber(source).sync()

    assert stats.failed == 1
    assert (tmp_path / "raw/a.md").read_bytes() == POD
    assert read_manifest(tmp_path)["a.md"]["sha"] == git_blob_sha(POD)


def test_corrupted_download_is_rejected(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD}, corrupt={"a.md": POD[:10]})

    stats = make_grabber(source).sync()

    assert stats.failed == 1
    assert not (tmp_path / "raw/a.md").exists()


def test_duplicate_content_is_skipped(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD, "copy/a.md": POD})

    stats = make_grabber(source).sync()

    assert (stats.added, stats.duplicates) == (1, 1)
    assert set(read_manifest(tmp_path)) == {"a.md"}


def test_missing_local_file_is_restored(make_grabber, tmp_path):
    source = FakeSource({"a.md": POD})
    make_grabber(source).sync()
    (tmp_path / "raw/a.md").unlink()

    stats = make_grabber(source).sync()

    assert stats.updated == 1
    assert (tmp_path / "raw/a.md").exists()


def test_dry_run_writes_nothing(make_grabber, tmp_path):
    stats = make_grabber(FakeSource({"a.md": POD})).sync(dry_run=True)

    assert stats.added == 1
    assert not (tmp_path / "manifest.json").exists()
    assert not (tmp_path / "raw").exists()


@pytest.mark.parametrize(
    ("path", "url"),
    [
        ("concepts/workloads/pods/_index.md", f"{SITE}/concepts/workloads/pods/"),
        ("concepts/overview/components.md", f"{SITE}/concepts/overview/components/"),
        ("concepts/_index.md", f"{SITE}/concepts/"),
        ("tasks/foo_index.md", f"{SITE}/tasks/foo_index/"),
    ],
)
def test_page_url(path, url):
    assert page_url(SITE, path) == url


def test_front_matter_is_split_from_body():
    front, body = split_front_matter("---\r\ntitle: Pods\r\n---\r\nBody\r\n")
    assert front == {"title": "Pods"}
    assert body == "Body\n"


def test_broken_front_matter_falls_back_to_heading(make_grabber, tmp_path):
    source = FakeSource({"x/page.md": b"---\ntitle: [unclosed\n---\n# Real Title\ntext\n"})

    make_grabber(source).sync()

    assert read_manifest(tmp_path)["x/page.md"]["title"] == "Real Title"
