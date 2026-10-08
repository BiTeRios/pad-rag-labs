"""Сборка образов сервисов Lab2 и загрузка их в Minikube.

    python docker/build_images.py                          # docker build + minikube image load (все 8 образов)
    python docker/build_images.py auth-service gateway     # выборочно
    python docker/build_images.py --no-load                # только собрать (Docker Compose или свой registry)

Dockerfile лежит у каждого сервиса в Lab2 (services/<name>/Dockerfile, gateway/Dockerfile); контекст сборки —
корень lab2 (нужна общая библиотека libs/common, лишнее отсекает lab2/.dockerignore).
Тег — rag/<name>:<IMAGE_TAG> (по умолчанию 1.0.0): тот же в docker-compose.yml Lab2 и в манифестах k8s/.
Повторная сборка без изменений берёт все слои из кэша; minikube image load копирует образ в узел кластера.
"""

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

LAB2 = Path(__file__).resolve().parents[2] / "lab2"
DOCKERFILES = {
    "auth-service": "services/auth-service/Dockerfile",
    "ingestion-service": "services/ingestion-service/Dockerfile",
    "inference-service": "services/inference-service/Dockerfile",
    "indexing-service": "services/indexing-service/Dockerfile",
    "retrieval-service": "services/retrieval-service/Dockerfile",
    "chat-service": "services/chat-service/Dockerfile",
    "analytics-service": "services/analytics-service/Dockerfile",
    "gateway": "gateway/Dockerfile",
}


def run(*command: str) -> None:
    print("  $", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Сборка образов и загрузка в Minikube")
    parser.add_argument("services", nargs="*", help=f"по умолчанию — все: {', '.join(DOCKERFILES)}")
    parser.add_argument("--tag", default=os.getenv("IMAGE_TAG", "1.0.0"))
    parser.add_argument("--no-load", action="store_true", help="не загружать в Minikube")
    args = parser.parse_args()
    if unknown := set(args.services) - set(DOCKERFILES):
        parser.error(f"неизвестные сервисы: {', '.join(sorted(unknown))}")

    minikube = shutil.which("minikube")
    if not args.no_load and minikube is None:
        sys.exit("minikube не найден в PATH (или запустите с --no-load)")
    for name in args.services or DOCKERFILES:
        image = f"rag/{name}:{args.tag}"
        started = time.perf_counter()
        print(f"=== {image}")
        run("docker", "build", "-f", str(LAB2 / DOCKERFILES[name]), "-t", image, str(LAB2))
        if not args.no_load:
            run(minikube, "image", "load", image)
        print(f"  готово за {time.perf_counter() - started:.0f} с")
    return 0


if __name__ == "__main__":
    sys.exit(main())
