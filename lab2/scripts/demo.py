"""Демонстрационный сценарий через gateway: auth → сбор корпуса → индекс → поиск → ответы → история → аналитика.

    python scripts/demo.py [--base-url http://localhost:8000] [--skip-sync]

Пароль admin берётся из DEMO_ADMIN_EMAIL / DEMO_ADMIN_PASSWORD или из .local/secrets.json (scripts/run_local.py).
Без RabbitMQ (run_local) индекс обновляется через POST /api/indexing/reconcile — сценарий делает это сам.
"""

import argparse
import json
import os
import sys
import time
import uuid
from pathlib import Path

import httpx

LAB2 = Path(__file__).resolve().parent.parent
QUESTIONS = [
    "Как ограничить потребление памяти контейнером?",
    "Чем Deployment отличается от StatefulSet?",
    "Как приготовить борщ?",  # вне базы: отказ без вызова LLM
]


def admin_credentials() -> tuple[str, str]:
    if os.getenv("DEMO_ADMIN_PASSWORD"):
        return os.getenv("DEMO_ADMIN_EMAIL", "admin@example.com"), os.environ["DEMO_ADMIN_PASSWORD"]
    keys = json.loads((LAB2 / ".local" / "secrets.json").read_text(encoding="utf-8"))
    return keys["admin_email"], keys["admin_password"]


def step(title: str) -> None:
    print(f"\n=== {title}")


def show(response: httpx.Response, note: str = "") -> dict:
    body = response.json() if response.content else {}
    error = body.get("error") if isinstance(body, dict) else None
    detail = f"{error['code']}: {error['message']}" if error else note
    print(f"  {response.request.method} {response.request.url.path} → {response.status_code} {detail}".rstrip())
    return body


def wait(predicate, timeout_s: float, step_s: float = 3.0):
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        if result := predicate():
            return result
        time.sleep(step_s)
    raise TimeoutError("не дождались")


def main() -> int:
    parser = argparse.ArgumentParser(description="Демонстрация Lab2 через gateway")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--skip-sync", action="store_true", help="не запускать синхронизацию корпуса")
    parser.add_argument("--timeout", type=float, default=1200)
    args = parser.parse_args()
    api = httpx.Client(base_url=args.base_url, timeout=200)

    step("Готовность сервисов (агрегация /ready)")
    print("  ", api.get("/api/status").json())

    step("Аутентификация и авторизация")
    email, password = admin_credentials()
    admin = {"Authorization": "Bearer " + show(api.post("/api/auth/login", json={"email": email, "password": password}),
                                               "admin вошёл")["access_token"]}
    user_credentials = {"email": f"demo-{uuid.uuid4().hex[:6]}@example.com", "password": "demo-password"}
    show(api.post("/api/auth/register", json=user_credentials), "пользователь создан")
    user = {"Authorization": "Bearer " + api.post("/api/auth/login", json=user_credentials).json()["access_token"]}
    show(api.post("/api/auth/register", json=user_credentials))  # повтор → 409
    show(api.get("/api/chat/conversations"))  # без токена → 401
    show(api.post("/api/ingestion/runs", headers=user))  # не admin → 403
    show(api.get("/api/auth/me", headers=user), "профиль по токену")

    before = (api.get("/api/indexing/status", headers=admin).json()["last_job"] or {}).get("started_at")
    if not args.skip_sync:
        step("Сбор корпуса из GitHub (ingestion-service, в фоне)")
        started = time.perf_counter()
        run = show(api.post("/api/ingestion/runs", headers=admin), "запуск принят")
        if "id" in run:
            run = wait(lambda: (r := api.get(f"/api/ingestion/runs/{run['id']}", headers=admin).json())["status"] != "running" and r,
                       args.timeout)
            print(f"  итог: {run['status']}, добавлено {run['added']}, обновлено {run['updated']}, без изменений {run['unchanged']}, "
                  f"удалено {run['deleted']}, дублей {run['duplicates']}, ошибок {run['failed']} — {time.perf_counter() - started:.0f} с")

    step("Индексация (indexing-service → inference-service → Qdrant)")
    started = time.perf_counter()
    def event_job() -> bool:  # documents.changed дошло до indexing-service через RabbitMQ
        status = api.get("/api/indexing/status", headers=admin).json()
        return bool(status["running"] or (status["last_job"] or {}).get("started_at") != before)

    try:
        wait(event_job, 20, 1)
        print("  индексация запущена событием documents.changed")
    except TimeoutError:  # без брокера (run_local.py) события нет — сверяем вручную
        show(api.post("/api/indexing/reconcile", headers=admin), "сверка индекса с корпусом")
        time.sleep(1)
    status = wait(lambda: (s := api.get("/api/indexing/status", headers=admin).json())["running"] is None and s, args.timeout)
    job = status["last_job"] or {}
    print(f"  коллекция {status['collection']}: документов {status['documents']}, chunks {status['points']}; "
          f"задача {job.get('trigger')} {job.get('status')} за {job.get('duration_s')} с ({time.perf_counter() - started:.0f} с)")
    print("  ", job.get("stats"))

    step("Семантический поиск (retrieval-service)")
    found = show(api.post("/api/search", json={"query": QUESTIONS[0]}, headers=user))
    print(f"  шаги: {found['stages']}, задержки, мс: {found['timings_ms']}, degraded: {found['degraded']}")
    for chunk in found["chunks"][:3]:
        print(f"    {chunk['rerank_score']:.3f}  {chunk['heading'][:90]}")

    step("Вопросы (chat-service → retrieval → LLM)")
    conversation_id = None
    for question in QUESTIONS:
        response = api.post("/api/chat/ask", json={"question": question, "conversation_id": conversation_id}, headers=user)
        message = show(response)
        if "id" not in message:
            continue
        conversation_id = conversation_id or message["conversation_id"]
        print(f"  Вопрос: {question}")
        print(f"  Ответ ({'отказ' if message['refused'] else message['model']}, {message['timings_ms']} мс, "
              f"request_id {response.headers['X-Request-ID'][:8]}…):")
        print("    " + message["answer"].replace("\n", "\n    "))
        for source in message["sources"]:
            print(f"    [{source['n']}] {source['title']} — {source['url']}")

    step("История и аналитика")
    history = api.get(f"/api/chat/conversations/{conversation_id}", headers=user).json()
    print(f"  диалог: {len(history['messages'])} сообщения")
    show(api.get(f"/api/chat/conversations/{conversation_id}", headers=admin), "admin видит диалог")
    show(api.post("/api/feedback", json={"message_id": history["messages"][0]["id"], "rating": 1}, headers=user))
    summary = show(api.get("/api/analytics/summary", headers=admin), "сводка")
    print(f"  вопросов {summary.get('questions')}, доля отказов {summary.get('refusal_rate')}, "
          f"задержка {summary.get('latency_ms')}, последнее обновление индекса: {bool(summary.get('last_index_update'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
