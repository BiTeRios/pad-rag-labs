"""Разделение Markdown на код и прозу: очистка и нормализация не должны трогать содержимое кода."""

import re

_FENCE_OPEN = re.compile(r"^\s*(```|~~~)")


def split_code(text: str) -> list[tuple[bool, str]]:
    """[(is_code, segment), ...]; "\\n".join(сегментов) восстанавливает исходный текст."""
    segments: list[tuple[bool, str]] = []
    buffer: list[str] = []
    fence = ""

    def flush(is_code: bool) -> None:
        if buffer:
            segments.append((is_code, "\n".join(buffer)))
            buffer.clear()

    for line in text.split("\n"):
        if not fence:
            match = _FENCE_OPEN.match(line)
            if match:
                flush(False)
                fence = match.group(1)
            buffer.append(line)
        else:
            buffer.append(line)
            if line.strip().startswith(fence) and not line.strip().strip(fence[0]):
                flush(True)
                fence = ""
    flush(bool(fence))  # незакрытый блок кода считается кодом до конца текста
    return segments
