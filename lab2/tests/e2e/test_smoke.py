"""Сквозной сценарий против запущенного docker compose (через gateway).

Запуск: E2E_BASE_URL=http://localhost:8000 E2E_ADMIN_EMAIL=... E2E_ADMIN_PASSWORD=... pytest tests/e2e
Без E2E_BASE_URL тесты пропускаются (в обычном `pytest` они не нужны).
E2E_NO_BROKER=1 — система запущена без RabbitMQ (scripts/run_local.py): индекс обновляется через
POST /api/indexing/reconcile, проверки событий в analytics пропускаются.

Сценарий: регистрация и вход → 401/403 → синхронизация корпуса (admin) → событие → индекс →
поиск → вопрос → ответ с источниками и отказ вне базы → оценка → аналитика по событиям.
"""

import os
import time
import uuid

import httpx
import pytest

BASE_URL = os.getenv("E2E_BASE_URL")
pytestmark = pytest.mark.skipif(not BASE_URL, reason="E2E_BASE_URL не задан: нужен запущенный docker compose")

SYNC_TIMEOUT_S = float(os.getenv("E2E_SYNC_TIMEOUT_S", "900"))
BROKER = os.getenv("E2E_NO_BROKER") != "1"
needs_broker = pytest.mark.skipif(not BROKER, reason="без RabbitMQ события между сервисами не передаются")


@pytest.fixture(scope="module")
def api():
    with httpx.Client(base_url=BASE_URL, timeout=200) as client:
        yield client


def login(api, email, password) -> dict:
    response = api.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture(scope="module")
def admin(api) -> dict:
    return login(api, os.environ["E2E_ADMIN_EMAIL"], os.environ["E2E_ADMIN_PASSWORD"])


@pytest.fixture(scope="module")
def user(api) -> dict:
    credentials = {"email": f"e2e-{uuid.uuid4().hex[:8]}@example.com", "password": "e2e-password"}
    assert api.post("/api/auth/register", json=credentials).status_code == 201
    return login(api, **credentials)


def wait(predicate, timeout_s: float, step_s: float = 3.0):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if value := predicate():
            return value
        time.sleep(step_s)
    raise AssertionError("не дождались")


def test_all_services_ready(api):
    status = api.get("/api/status").json()
    assert status["status"] == "ok", status


def test_auth_errors(api, user):
    assert api.get("/api/chat/conversations").status_code == 401
    assert api.get("/api/analytics/summary", headers=user).status_code == 403
    assert api.post("/api/ingestion/runs", headers=user).status_code == 403


def test_ingestion_event_reaches_index(api, admin):
    run = api.post("/api/ingestion/runs", headers=admin)
    assert run.status_code in (202, 409), run.text
    if run.status_code == 202:
        finished = wait(lambda: (r := api.get(f"/api/ingestion/runs/{run.json()['id']}", headers=admin).json())["status"] != "running" and r,
                        SYNC_TIMEOUT_S)
        assert finished["status"] in ("succeeded", "partial"), finished
    if not BROKER:  # события documents.changed нет — сверка индекса вручную
        wait(lambda: api.post("/api/indexing/reconcile", headers=admin).status_code == 202, SYNC_TIMEOUT_S)
        time.sleep(2)
    # documents.changed → indexing-service (или сверка): индекс не пуст и задача завершилась
    state = wait(lambda: (s := api.get("/api/indexing/status", headers=admin).json())["points"] and not s["running"] and s,
                 SYNC_TIMEOUT_S)
    assert state["documents"] > 0 and state["last_job"]["status"] == "succeeded"


def test_search_and_answer_with_sources(api, user):
    found = api.post("/api/search", json={"query": "Как ограничить потребление памяти контейнером?"}, headers=user).json()
    assert found["chunks"], found

    answer = api.post("/api/chat/ask", json={"question": "Как ограничить потребление памяти контейнером?"}, headers=user)
    assert answer.status_code == 200, answer.text
    message = answer.json()
    assert message["refused"] is False and message["sources"] and answer.headers["X-Request-ID"]

    refusal = api.post("/api/chat/ask", json={"question": "Как приготовить борщ?"}, headers=user).json()
    assert refusal["refused"] is True and refusal["model"] is None  # LLM не вызывалась


@needs_broker
def test_feedback_after_question_answered_event(api, user):
    message = api.post("/api/chat/ask", json={"question": "Что такое Pod?"}, headers=user).json()
    # question.answered → analytics-service: оценка принимается, когда событие обработано
    rated = wait(lambda: (r := api.post("/api/feedback", json={"message_id": message["id"], "rating": 1},
                                        headers=user)).status_code in (200, 201) and r, 30, 1)
    assert rated.json()["rating"] == 1


@needs_broker
def test_analytics_sees_events(api, admin):
    summary = api.get("/api/analytics/summary", headers=admin).json()
    assert summary["questions"] >= 2 and summary["feedback"]["count"] >= 1
    assert summary["users_registered"] >= 1 and summary["last_index_update"] is not None
