from ingestion_helpers import run_sync, wait_run

from rag_common.testing import as_admin, as_user

PODS = "concepts/workloads/pods/_index.md"
SERVICE = "concepts/services-networking/service.md"


def test_first_sync_stores_documents_with_metadata_and_publishes_event(client, bus):
    run = run_sync(client)
    assert (run["status"], run["added"], run["failed"]) == ("succeeded", 3, 0)

    document = client.get(f"/api/ingestion/documents/{PODS}", headers=as_user()).json()
    assert document["title"] == "Pods" and document["url"] == "https://kubernetes.io/docs/concepts/workloads/pods/"
    assert document["section"] == "concepts/workloads/pods" and "smallest" in document["content"]
    assert client.get(f"/internal/documents/{SERVICE}").json()["title"] == "Service"  # заголовок из «# Service»

    [event] = bus.of_type("documents.changed")
    assert sorted(event.payload["changed"]) == sorted([PODS, SERVICE, "tasks/run-application/run-stateless.md"])
    assert event.payload["deleted"] == [] and event.payload["run_id"] == run["id"]


def test_repeated_sync_is_incremental(client, source, bus):
    run_sync(client)
    source.fetched.clear()

    again = run_sync(client)
    assert (again["added"], again["updated"], again["unchanged"]) == (0, 0, 3)
    assert source.fetched == [] and len(bus.of_type("documents.changed")) == 1  # без изменений — без события

    source.files[PODS] = "---\ntitle: Pods\n---\nPods are updated."
    del source.files[SERVICE]
    changed = run_sync(client)
    assert (changed["updated"], changed["deleted"], changed["unchanged"]) == (1, 1, 1)
    assert source.fetched == [PODS]
    event = bus.of_type("documents.changed")[-1]
    assert event.payload["changed"] == [PODS] and event.payload["deleted"] == [SERVICE]
    assert client.get(f"/api/ingestion/documents/{SERVICE}", headers=as_user()).status_code == 404


def test_duplicates_and_corrupted_files_are_skipped(client, source):
    source.files["tasks/copy-of-pods.md"] = source.files[PODS]
    source.broken.add(SERVICE)
    run = run_sync(client)
    assert (run["status"], run["added"], run["duplicates"], run["failed"]) == ("partial", 2, 1, 1)

    source.broken.clear()
    retry = run_sync(client)  # повторный запуск докачивает пропущенное
    assert (retry["status"], retry["added"]) == ("succeeded", 1)


def test_only_one_run_at_a_time_and_admin_only(client, source):
    assert client.post("/api/ingestion/runs", headers=as_user()).status_code == 403
    assert client.post("/api/ingestion/runs").status_code == 401

    source.gate.clear()  # первый запуск «зависает» на скачивании
    first = client.post("/api/ingestion/runs", headers=as_admin()).json()
    second = client.post("/api/ingestion/runs", headers=as_admin())
    assert second.status_code == 409 and second.json()["error"]["code"] == "sync_running"
    source.gate.set()
    assert wait_run(client, first["id"])["status"] == "succeeded"


def test_source_failure_marks_run_failed(client, source):
    source.snapshot = lambda: (_ for _ in ()).throw(RuntimeError("GitHub API недоступен"))
    run = run_sync(client)
    assert run["status"] == "failed" and "GitHub API недоступен" in run["error"]


def test_document_listing_filters_and_internal_endpoints(client):
    run_sync(client)
    page = client.get("/api/ingestion/documents", params={"section": "concepts"}, headers=as_user()).json()
    assert page["total"] == 2 and all(item["section"].startswith("concepts") for item in page["items"])
    assert "content" not in page["items"][0]
    assert client.get("/api/ingestion/documents", params={"q": "stateless"}, headers=as_user()).json()["total"] == 1

    fingerprints = client.get("/internal/documents").json()
    assert len(fingerprints) == 3 and set(fingerprints[0]) == {"id", "sha"}
    batch = client.post("/internal/documents/batch", json={"ids": [PODS, "missing.md"]}).json()
    assert [document["id"] for document in batch] == [PODS]
    assert client.post("/internal/documents/batch", json={"ids": []}).status_code == 422


def test_changes_are_published_in_batches(tmp_path, source, bus):
    from fastapi.testclient import TestClient

    from ingestion_service.config import Settings
    from ingestion_service.main import create_app

    settings = Settings(database_url=f"sqlite+aiosqlite:///{tmp_path / 'b.db'}", rabbitmq_url=None, event_batch_size=2)
    with TestClient(create_app(settings, event_bus=bus, source=source)) as client:
        run_sync(client)
        events = bus.of_type("documents.changed")
        assert [(e.payload["batch"], e.payload["batches"], len(e.payload["changed"])) for e in events] == [(1, 2, 2), (2, 2, 1)]

        del source.files[SERVICE]
        run_sync(client)  # только удаление — одна пачка без изменённых
        assert bus.of_type("documents.changed")[-1].payload | {"run_id": None} == {
            "run_id": None, "commit_sha": "1".zfill(40), "changed": [], "deleted": [SERVICE], "batch": 1, "batches": 1}
