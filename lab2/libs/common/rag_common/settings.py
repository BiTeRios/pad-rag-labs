"""Типы для настроек из переменных окружения."""

from typing import Annotated

from pydantic import BeforeValidator
from pydantic_settings import NoDecode


def _split(value):
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    return value


# Список через запятую: SECTIONS=concepts,tasks,tutorials (вместо JSON-строки)
CommaList = Annotated[list[str], NoDecode, BeforeValidator(_split)]
