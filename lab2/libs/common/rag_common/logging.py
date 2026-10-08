"""Структурированные логи: одна JSON-строка на событие, в каждой — timestamp, service, level, request_id, message."""

import json
import logging
import sys
from contextvars import ContextVar
from datetime import UTC, datetime

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)

# Атрибуты LogRecord, которые не выводятся как дополнительные поля.
_STANDARD = set(logging.LogRecord("", 0, "", 0, "", None, None).__dict__) | {"message", "asctime", "taskName", "ctx_request_id"}
_NOISY = ("httpx", "httpcore", "aio_pika", "aiormq", "urllib3", "huggingface_hub", "sentence_transformers")


class JsonFormatter(logging.Formatter):
    def __init__(self, service: str):
        super().__init__()
        self.service = service

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "service": self.service,
            "level": record.levelname,
            "request_id": getattr(record, "request_id", None) or getattr(record, "ctx_request_id", None)
            or request_id_var.get(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        # extra={...} из вызова логгера: method, path, status, duration_ms, event и т.п.
        payload.update({k: v for k, v in record.__dict__.items() if k not in _STANDARD and k not in payload})
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)  # stack trace — только в логах
        return json.dumps(payload, ensure_ascii=False, default=str)


def _install_record_factory() -> None:
    """request_id запоминается при создании записи: верен, даже если запись форматируется позже, вне запроса."""
    base = logging.getLogRecordFactory()
    if getattr(base, "with_request_id", False):
        return

    def factory(*args, **kwargs):
        record = base(*args, **kwargs)
        record.ctx_request_id = request_id_var.get()
        return record

    factory.with_request_id = True
    logging.setLogRecordFactory(factory)


def setup_logging(service: str, level: str = "INFO") -> None:
    _install_record_factory()
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter(service))
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level.upper())
    # uvicorn настраивает свои логгеры до импорта приложения: переводим их на общий JSON-формат.
    for name in ("uvicorn", "uvicorn.error"):
        logger = logging.getLogger(name)
        logger.handlers = []
        logger.propagate = True
    logging.getLogger("uvicorn.access").disabled = True  # доступ логирует RequestContextMiddleware
    for name in _NOISY:
        logging.getLogger(name).setLevel(logging.WARNING)
