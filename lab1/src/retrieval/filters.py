"""Фильтры контекста. Каждый получает chunks по убыванию релевантности и сохраняет порядок."""

import re

_WORD = re.compile(r"\w+")


def body_text(chunk: dict) -> str:
    """Текст chunk без префикса «Title > Section\\n\\n», если он был добавлен при chunking."""
    return chunk["text"].removeprefix(f"{chunk.get('heading', '')}\n\n").strip()


def by_score(chunks: list[dict], threshold: float, key: str = "score") -> list[dict]:
    """Отбрасывает chunks со score ниже порога; threshold <= 0 выключает фильтр."""
    if threshold <= 0:
        return chunks
    return [chunk for chunk in chunks if chunk[key] >= threshold]


def by_min_length(chunks: list[dict], min_chars: int) -> list[dict]:
    """Отбрасывает слишком короткие chunks («See X for more information.»)."""
    return [chunk for chunk in chunks if len(body_text(chunk)) >= min_chars]


def deduplicate(chunks: list[dict], threshold: float) -> list[dict]:
    """Убирает дубли и почти-дубли: Jaccard по 3-словным шинглам >= threshold.

    Остаётся первый, то есть более релевантный, из группы. threshold = 1.0 убирает только
    точные дубли, threshold <= 0 выключает фильтр.
    """
    if threshold <= 0:
        return chunks
    kept: list[tuple[dict, set]] = []
    for chunk in chunks:
        shingles = _shingles(body_text(chunk))
        if all(_jaccard(shingles, other) < threshold for _, other in kept):
            kept.append((chunk, shingles))
    return [chunk for chunk, _ in kept]


def limit_per_document(chunks: list[dict], max_per_document: int) -> list[dict]:
    """Не больше N chunks из одного документа, чтобы контекст не состоял из одной страницы; 0 — без лимита."""
    if max_per_document <= 0:
        return chunks
    counts: dict[str, int] = {}
    result = []
    for chunk in chunks:
        count = counts.get(chunk["document_id"], 0)
        if count < max_per_document:
            counts[chunk["document_id"]] = count + 1
            result.append(chunk)
    return result


def _shingles(text: str, size: int = 3) -> set:
    words = _WORD.findall(text.lower())
    if len(words) < size:
        return {tuple(words)}
    return {tuple(words[i:i + size]) for i in range(len(words) - size + 1)}


def _jaccard(a: set, b: set) -> float:
    return len(a & b) / len(a | b) if a or b else 1.0
