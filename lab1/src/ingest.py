"""Обновление базы знаний одной командой: grabber → preprocessing → embeddings.

Запуск: python -m src.ingest [--config PATH] [--log-level LEVEL]
Каждый шаг инкрементальный: повторный запуск без изменений в источнике ничего не скачивает
и не векторизует. Параметры (chunking, модель эмбеддингов) берутся из config.

Коды выхода: 0 — успех; иначе код первого неуспешного шага. Частичная загрузка grabber (код 2)
индексацию не останавливает: корпус пригоден, итоговый код будет 2.
"""

import argparse
import sys
import time

from src.embeddings.__main__ import main as embeddings_main
from src.grabber.__main__ import main as grabber_main
from src.preprocessing.__main__ import main as preprocessing_main

STEPS = (("grabber", grabber_main), ("preprocessing", preprocessing_main), ("embeddings", embeddings_main))
GRABBER_PARTIAL = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Сбор документов, очистка, chunking и индексация")
    parser.add_argument("--config", help="YAML-конфиг (по умолчанию configs/config.yaml)")
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args(argv)

    common = (["--config", args.config] if args.config else []) + ["--log-level", args.log_level]
    status = 0
    for name, step in STEPS:
        started = time.perf_counter()
        code = step(list(common))
        print(f"[ingest] {name}: код {code}, {time.perf_counter() - started:.0f} с", flush=True)
        if name == "grabber" and code == GRABBER_PARTIAL:
            status = code
        elif code != 0:
            return code
    return status


if __name__ == "__main__":
    sys.exit(main())
