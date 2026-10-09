"""Секреты для self-hosted Langfuse: langfuse/.env (сервер) и ключи API в lab1/.env (клиент).

    python langfuse/make_env.py           # создать, если файла ещё нет
    python langfuse/make_env.py --force   # пересоздать (только вместе с docker compose down -v: пароли хранятся в томах)

Пароли и ключи случайные (secrets), в git не попадают: оба .env в .gitignore.
"""

import argparse
import secrets
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SERVER_ENV = HERE / ".env"
CLIENT_ENV = HERE.parent / ".env"
ADMIN_EMAIL = "admin@lab1.local"


def server_values() -> dict[str, str]:
    return {
        "POSTGRES_PASSWORD": secrets.token_hex(16),
        "CLICKHOUSE_PASSWORD": secrets.token_hex(16),
        "REDIS_AUTH": secrets.token_hex(16),
        "MINIO_ROOT_PASSWORD": secrets.token_hex(16),
        "SALT": secrets.token_hex(16),
        "ENCRYPTION_KEY": secrets.token_hex(32),
        "NEXTAUTH_SECRET": secrets.token_hex(32),
        "LANGFUSE_INIT_PROJECT_PUBLIC_KEY": f"pk-lf-{secrets.token_hex(16)}",
        "LANGFUSE_INIT_PROJECT_SECRET_KEY": f"sk-lf-{secrets.token_hex(16)}",
        "LANGFUSE_INIT_USER_EMAIL": ADMIN_EMAIL,
        "LANGFUSE_INIT_USER_PASSWORD": secrets.token_urlsafe(12),
    }


def read_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}
    pairs = (line.split("=", 1) for line in path.read_text(encoding="utf-8").splitlines() if "=" in line)
    return {key.strip(): value.strip() for key, value in pairs if not key.lstrip().startswith("#")}


def set_env_values(path: Path, values: dict[str, str]) -> None:
    """Заменяет или дописывает ключи, остальные строки (GITHUB_TOKEN и комментарии) не трогает."""
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    rest = dict(values)
    for i, line in enumerate(lines):
        key = line.split("=", 1)[0].strip()
        if key in rest:
            lines[i] = f"{key}={rest.pop(key)}"
    lines += [f"{key}={value}" for key, value in rest.items()]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Секреты self-hosted Langfuse")
    parser.add_argument("--force", action="store_true", help="пересоздать langfuse/.env")
    args = parser.parse_args(argv)

    if SERVER_ENV.exists() and not args.force:
        print(f"{SERVER_ENV} уже есть — оставлен как есть (пересоздать: --force вместе с docker compose down -v)")
    else:
        set_env_values(SERVER_ENV, server_values())
        print(f"Создан {SERVER_ENV}")

    server = read_env(SERVER_ENV)
    set_env_values(CLIENT_ENV, {
        "LANGFUSE_PUBLIC_KEY": server["LANGFUSE_INIT_PROJECT_PUBLIC_KEY"],
        "LANGFUSE_SECRET_KEY": server["LANGFUSE_INIT_PROJECT_SECRET_KEY"],
    })
    print(f"Ключи API проекта lab1-rag записаны в {CLIENT_ENV}")
    print(f"Вход в UI: {server['LANGFUSE_INIT_USER_EMAIL']}, пароль — LANGFUSE_INIT_USER_PASSWORD в {SERVER_ENV}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
