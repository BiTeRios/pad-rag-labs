"""Создаёт k8s/secrets/secret.yaml из шаблона secret.example.yaml со случайными паролями.

    python scripts/make_secret.py            # не перезаписывает существующий secret.yaml
    python scripts/make_secret.py --force    # новые пароли (PostgreSQL в своём томе останется со старыми!)

secret.yaml в .gitignore. ADMIN_EMAIL берётся из шаблона, GITHUB_TOKEN — из переменной окружения (если задана).
"""

import argparse
import os
import re
import secrets
import sys
from pathlib import Path

SECRETS = Path(__file__).resolve().parent.parent / "k8s" / "secrets"
TEMPLATE, TARGET = SECRETS / "secret.example.yaml", SECRETS / "secret.yaml"
KEEP = {"ADMIN_EMAIL"}
VALUE = re.compile(r"^(  )([A-Z][A-Z0-9_]*): (.*)$")


def value_for(key: str, template_value: str) -> str:
    if key in KEEP:
        return template_value
    if key == "GITHUB_TOKEN":
        return f'"{os.getenv("GITHUB_TOKEN", "")}"'
    return f'"{secrets.token_urlsafe(48 if key == "JWT_SECRET" else 18)}"'  # только [A-Za-z0-9_-]: пароли идут в URL


def main() -> int:
    parser = argparse.ArgumentParser(description="Secret со случайными паролями")
    parser.add_argument("--force", action="store_true", help="перезаписать существующий secret.yaml")
    args = parser.parse_args()
    if TARGET.exists() and not args.force:
        print(f"{TARGET.name} уже есть — оставлен без изменений (--force, чтобы пересоздать)")
        return 0

    lines = []
    for line in TEMPLATE.read_text(encoding="utf-8").splitlines():
        if line.startswith("#"):
            continue  # комментарии шаблона про git не относятся к настоящему файлу
        if match := VALUE.match(line):
            indent, key, template_value = match.groups()
            line = f"{indent}{key}: {value_for(key, template_value)}"
        lines.append(line)
    header = "# Сгенерировано scripts/make_secret.py. НЕ коммитить (файл в .gitignore).\n"
    TARGET.write_text(header + "\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"создан {TARGET.relative_to(SECRETS.parent.parent)}; пароль admin: kubectl get secret rag-secrets -n rag "
          "-o jsonpath='{.data.ADMIN_PASSWORD}' | base64 -d")
    return 0


if __name__ == "__main__":
    sys.exit(main())
