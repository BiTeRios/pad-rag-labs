"""Нормализация текста: unicode, пробелы, переносы строк.

Регистр сохраняется: embedding-модели учитывают его сами, а для LLM исходный текст читабельнее.
"""

import re
import unicodedata

from indexing_service.preprocessing.segments import split_code

_INVISIBLE = dict.fromkeys(map(ord, "​‌‍⁠﻿­"), None)
_QUOTES = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})
_INNER_SPACES = re.compile(r"(?<=\S) {2,}")
_BLOCK_START = re.compile(r"^(#{1,6}\s|[-*+]\s|\d+[.)]\s|\||>)")
_NO_CONTINUATION = re.compile(r"^(#{1,6}\s|\|)")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).translate(_INVISIBLE).translate(_QUOTES)
    text = text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", "    ")
    parts = []
    for is_code, segment in split_code(text):
        if is_code:
            parts.append("\n".join(line.rstrip() for line in segment.split("\n")))
        else:
            parts.append(_normalize_prose(segment))
    text = "\n".join(parts)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _normalize_prose(segment: str) -> str:
    """Склеивает строки, разбитые переносом в исходнике, и схлопывает лишние пробелы.

    Заголовки, элементы списков, строки таблиц и цитаты остаются отдельными строками.
    """
    lines: list[str] = []
    for raw_line in segment.split("\n"):
        line = _INNER_SPACES.sub(" ", raw_line.rstrip())
        stripped = line.lstrip()
        if not stripped:
            lines.append("")
            continue
        previous = lines[-1].lstrip() if lines else ""
        if previous and not _BLOCK_START.match(stripped) and not _NO_CONTINUATION.match(previous):
            lines[-1] = f"{lines[-1]} {stripped}"
        else:
            lines.append(line)
    return "\n".join(lines)
