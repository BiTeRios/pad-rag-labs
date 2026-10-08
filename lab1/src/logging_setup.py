"""Единая настройка логов для CLI-модулей: консоль + файл."""

import logging
from pathlib import Path

# Сторонние библиотеки на INFO пишут каждый HTTP-запрос к Hugging Face.
_NOISY_LOGGERS = ("httpx", "httpcore", "huggingface_hub", "sentence_transformers", "urllib3")


def setup_logging(log_file: Path, level: str = "INFO") -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[logging.StreamHandler(), logging.FileHandler(log_file, encoding="utf-8")],
        force=True,  # src.ingest вызывает несколько CLI подряд: у каждого шага свой лог-файл
    )
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)
