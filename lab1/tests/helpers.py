"""Детерминированные замены моделей для тестов: без сети, GPU и скачивания весов."""

import hashlib

import numpy as np

DIM = 64


def _words(text: str) -> list[str]:
    return [word for word in text.lower().split() if not word.endswith(":")]  # без префиксов query:/passage:


class BagOfWordsModel:
    """Замена SentenceTransformer: вектор = хеши слов. Запоминает все тексты."""

    def __init__(self):
        self.encoded: list[str] = []

    def get_embedding_dimension(self) -> int:
        return DIM

    def encode(self, texts, batch_size, normalize_embeddings, convert_to_numpy, show_progress_bar):
        self.encoded.extend(texts)
        vectors = np.zeros((len(texts), DIM), dtype=np.float32)
        for row, text in enumerate(texts):
            for word in _words(text):
                vectors[row, int(hashlib.md5(word.encode()).hexdigest(), 16) % DIM] += 1
        return vectors / np.maximum(np.linalg.norm(vectors, axis=1, keepdims=True), 1e-9)


class WordOverlapCrossEncoder:
    """Замена CrossEncoder: score = доля слов запроса, встречающихся в тексте."""

    def __init__(self):
        self.pairs: list[tuple[str, str]] = []

    def predict(self, pairs, batch_size, show_progress_bar):
        self.pairs.extend(pairs)
        scores = []
        for query, text in pairs:
            query_words, text_words = set(_words(query)), set(_words(text))
            scores.append(len(query_words & text_words) / max(len(query_words), 1))
        return np.array(scores, dtype=np.float32)


def make_chunk(doc_id: str, index: int, text: str, sha: str = "v1", section: str = "concepts", **extra) -> dict:
    return {
        "chunk_id": f"{doc_id}#{index}",
        "document_id": doc_id,
        "chunk_index": index,
        "text": text,
        "heading": doc_id,
        "url": f"https://kubernetes.io/docs/{doc_id}/",
        "title": doc_id,
        "section": section,
        "source": "kubernetes-docs",
        "updated_at": "2026-10-07T00:00:00+00:00",
        "doc_sha": sha,
        **extra,
    }
