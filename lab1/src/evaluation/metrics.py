"""Метрики retrieval по ранжированному списку document_id найденных chunks.

Релевантность размечена на уровне документов: chunk релевантен, если он из релевантного документа.
- Hit@K       — есть ли в top-K хотя бы один релевантный chunk;
- Recall@K    — доля релевантных документов, попавших в top-K (для match=any: 1, если найден любой);
- Precision@K — доля релевантных среди возвращённых top-K chunks (фильтры могут вернуть меньше K);
- RR          — 1 / позиция первого релевантного chunk (0, если его нет); среднее по вопросам — MRR.
"""

from statistics import mean


def hit_at(ranked: list[str], relevant: set[str], k: int) -> float:
    return float(any(doc in relevant for doc in ranked[:k]))


def recall_at(ranked: list[str], relevant: set[str], k: int, match: str = "any") -> float:
    found = relevant & set(ranked[:k])
    if match == "all":
        return len(found) / len(relevant)
    return float(bool(found))


def precision_at(ranked: list[str], relevant: set[str], k: int) -> float:
    top = ranked[:k]
    return sum(doc in relevant for doc in top) / len(top) if top else 0.0


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    for position, doc in enumerate(ranked, 1):
        if doc in relevant:
            return 1 / position
    return 0.0


def retrieval_metrics(ranked: list[str], relevant: set[str], match: str, k_values: list[int]) -> dict[str, float]:
    metrics = {"rr": reciprocal_rank(ranked, relevant)}
    for k in k_values:
        metrics[f"hit@{k}"] = hit_at(ranked, relevant, k)
        metrics[f"recall@{k}"] = recall_at(ranked, relevant, k, match)
        metrics[f"precision@{k}"] = precision_at(ranked, relevant, k)
    return metrics


def average(rows: list[dict], key: str) -> float | None:
    values = [row[key] for row in rows if row.get(key) is not None]
    return round(mean(values), 4) if values else None
