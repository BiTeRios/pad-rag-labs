"""Запуск всех сервисов Lab2 без Docker — для разработки и демонстрации, пока Compose недоступен.

    python scripts/run_local.py [--fetch-limit N]   # запустить и ждать готовности (Ctrl+C — остановить)
    python scripts/run_local.py --detach            # запустить в фоне и выйти
    python scripts/run_local.py --stop              # остановить запущенные в фоне

Отличия от docker compose:
- вместо PostgreSQL — SQLite: у каждого сервиса свой файл в .local/, БД по-прежнему раздельные;
- вместо сервера Qdrant — локальный режим (папка .local/qdrant), как в Lab1: в индекс пишет только indexing-service;
- RabbitMQ нет: события остаются внутри процесса-издателя (InMemoryEventBus). Поэтому после синхронизации
  индекс обновляется через POST /api/indexing/reconcile, а analytics-service не получает данных.
Ollama — на хосте, как и в Compose. Логи сервисов (JSON) — .local/logs/<сервис>.log.
"""

import argparse
import json
import os
import secrets
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

LAB2 = Path(__file__).resolve().parent.parent
STATE = LAB2 / ".local"
SECRETS_FILE = STATE / "secrets.json"
PIDS_FILE = STATE / "pids.json"
HOST = "127.0.0.1"

# (имя, папка, пакет, порт) — порядок запуска
SERVICES = [
    ("auth", "services/auth-service", "auth_service", 8001),
    ("ingestion", "services/ingestion-service", "ingestion_service", 8002),
    ("inference", "services/inference-service", "inference_service", 8003),
    ("indexing", "services/indexing-service", "indexing_service", 8004),
    ("retrieval", "services/retrieval-service", "retrieval_service", 8005),
    ("chat", "services/chat-service", "chat_service", 8006),
    ("analytics", "services/analytics-service", "analytics_service", 8007),
    ("gateway", "gateway", "gateway_service", 8000),
]


def load_secrets() -> dict:
    """Секрет JWT и пароль admin создаются один раз и хранятся в .local/ (в git не попадает)."""
    if SECRETS_FILE.is_file():
        return json.loads(SECRETS_FILE.read_text(encoding="utf-8"))
    data = {"jwt_secret": secrets.token_urlsafe(48), "admin_email": "admin@example.com",
            "admin_password": secrets.token_urlsafe(12)}
    SECRETS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


def service_env(name: str, keys: dict, fetch_limit: int) -> dict:
    sqlite = lambda db: f"sqlite+aiosqlite:///{(STATE / f'{db}.db').as_posix()}"  # noqa: E731
    env = {**os.environ, "PYTHONUTF8": "1", "LOG_LEVEL": "INFO", "RABBITMQ_URL": ""}
    env.update({f"{other.upper()}_URL": f"http://{HOST}:{port}" for other, _, _, port in SERVICES if other != "gateway"})
    env.update({
        "auth": {"DATABASE_URL": sqlite("auth"), "JWT_SECRET": keys["jwt_secret"],
                 "ADMIN_EMAIL": keys["admin_email"], "ADMIN_PASSWORD": keys["admin_password"]},
        "ingestion": {"DATABASE_URL": sqlite("ingestion"), "FETCH_LIMIT": str(fetch_limit)},
        "inference": {},
        "indexing": {"QDRANT_PATH": str(STATE / "qdrant")},
        "retrieval": {},
        "chat": {"DATABASE_URL": sqlite("chat")},
        "analytics": {"DATABASE_URL": sqlite("analytics")},
        "gateway": {"JWT_SECRET": keys["jwt_secret"]},
    }[name])
    return env


def start(fetch_limit: int) -> list[subprocess.Popen]:
    (STATE / "logs").mkdir(parents=True, exist_ok=True)
    keys = load_secrets()
    processes = []
    for name, directory, package, port in SERVICES:
        log = (STATE / "logs" / f"{name}.log").open("ab")
        command = [sys.executable, "-m", "uvicorn", f"{package}.main:create_app", "--factory", "--host", HOST,
                   "--port", str(port)]
        flags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
        processes.append(subprocess.Popen(command, cwd=LAB2 / directory, env=service_env(name, keys, fetch_limit),
                                          stdout=log, stderr=subprocess.STDOUT, creationflags=flags))
        print(f"  {name:10} http://{HOST}:{port}  pid {processes[-1].pid}")
    PIDS_FILE.write_text(json.dumps([p.pid for p in processes]), encoding="utf-8")
    return processes


def status() -> dict | None:
    try:
        with urllib.request.urlopen(f"http://{HOST}:8000/api/status", timeout=5) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as error:  # 503 — часть сервисов ещё не готова
        return json.loads(error.read())
    except OSError:
        return None


def wait_ready(timeout_s: float) -> bool:
    deadline = time.monotonic() + timeout_s
    last = None
    while time.monotonic() < deadline:
        current = status()
        if current and current != last:
            print("  статус:", ", ".join(f"{k}={v}" for k, v in current["services"].items()))
            last = current
        if current and current["status"] == "ok":
            return True
        time.sleep(3)
    return False


def stop() -> None:
    if not PIDS_FILE.is_file():
        print("Запущенных сервисов нет")
        return
    for pid in json.loads(PIDS_FILE.read_text(encoding="utf-8")):
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, check=False)
            else:
                os.kill(pid, signal.SIGTERM)
        except OSError:
            pass
    PIDS_FILE.unlink()
    print("Сервисы остановлены")


def main() -> int:
    parser = argparse.ArgumentParser(description="Lab2 без Docker")
    parser.add_argument("--fetch-limit", type=int, default=0, help="не больше N документов за синхронизацию")
    parser.add_argument("--detach", action="store_true", help="запустить в фоне и выйти")
    parser.add_argument("--stop", action="store_true", help="остановить запущенные в фоне")
    parser.add_argument("--timeout", type=float, default=600, help="сколько ждать готовности, с")
    args = parser.parse_args()
    if args.stop:
        stop()
        return 0

    print("Запуск сервисов (логи — .local/logs):")
    processes = start(args.fetch_limit)
    keys = load_secrets()
    ready = wait_ready(args.timeout)
    print(("Готово" if ready else "Не все сервисы готовы, см. .local/logs") + f": gateway http://{HOST}:8000/docs")
    print(f"  admin: {keys['admin_email']} / пароль в {SECRETS_FILE.relative_to(LAB2)}")
    if args.detach:
        return 0 if ready else 1
    try:
        while all(p.poll() is None for p in processes):
            time.sleep(1)
        print("Один из сервисов завершился, см. .local/logs")
    except KeyboardInterrupt:
        pass
    stop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
