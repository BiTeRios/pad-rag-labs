"""Отделение YAML front matter Hugo от тела документа (из Lab1, src/grabber/metadata.py)."""

import logging
import re

import yaml

log = logging.getLogger(__name__)

_FRONT_MATTER = re.compile(r"\A﻿?---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)", re.DOTALL)


def split_front_matter(text: str) -> tuple[dict, str]:
    """Некорректный front matter даёт {}."""
    text = text.replace("\r\n", "\n")
    match = _FRONT_MATTER.match(text)
    if not match:
        return {}, text
    try:
        front = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as error:
        log.warning("Некорректный front matter: %s", error)
        front = {}
    return (front if isinstance(front, dict) else {}), text[match.end():]
