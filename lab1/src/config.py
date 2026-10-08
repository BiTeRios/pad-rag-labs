"""Загрузка конфигурации: configs/config.yaml и секреты из .env."""

from pathlib import Path

import yaml
from dotenv import load_dotenv

LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = LAB_ROOT / "configs" / "config.yaml"


def load_config(path: str | Path | None = None) -> dict:
    load_dotenv(LAB_ROOT / ".env")
    config_path = Path(path) if path else DEFAULT_CONFIG
    with config_path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def resolve_path(value: str | Path) -> Path:
    """Относительные пути из конфига считаются от корня lab1."""
    path = Path(value)
    return path if path.is_absolute() else LAB_ROOT / path
