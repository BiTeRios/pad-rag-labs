"""Соседи indexing-service на httpx.MockTransport: ingestion (документы) и inference (векторы bag-of-words)."""

import hashlib
import json
import math
import re

import httpx

from rag_common.events import InMemoryEventBus

DIM = 16


def bag_of_words(text: str) -> list[float]:
    vector = [0.0] * DIM
    for word in re.findall(r"\w+", text.lower()):
        if word not in ("query", "passage"):  # префиксы e5 не влияют на заглушку
            vector[int(hashlib.md5(word.encode()).hexdigest(), 16) % DIM] += 1
    norm = math.sqrt(sum(v * v for v in vector)) or 1.0
    return [v / norm for v in vector]


def make_document(doc_id: str, content: str, sha: str | None = None) -> dict:
    section = doc_id.rsplit("/", 1)[0]
    return {"id": doc_id, "sha": sha or hashlib.sha1(content.encode()).hexdigest(), "content": content,
            "source": "kubernetes-docs", "url": f"https://kubernetes.io/docs/{section}/", "title": doc_id.split("/")[-1],
            "section": section, "description": "", "size": len(content), "commit_sha": "c" * 40,
            "updated_at": "2026-10-08T00:00:00Z"}


class FakeNeighbours:
    def __init__(self, documents: list[dict]):
        self.documents = {document["id"]: document for document in documents}
        self.models_loaded = True
        self.embedded = 0

    def put(self, document: dict) -> None:
        self.documents[document["id"]] = document

    def ingestion(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/internal/documents":
                return httpx.Response(200, json=[{"id": d["id"], "sha": d["sha"]} for d in self.documents.values()])
            ids = json.loads(request.content)["ids"]
            return httpx.Response(200, json=[self.documents[i] for i in ids if i in self.documents])
        return httpx.MockTransport(handle)

    def inference(self) -> httpx.MockTransport:
        def handle(request: httpx.Request) -> httpx.Response:
            if request.url.path == "/internal/info":
                return httpx.Response(200, json={"loaded": self.models_loaded, "embedding_model": "intfloat/test-e5",
                                                 "dim": DIM})
            texts = json.loads(request.content)["texts"]
            self.embedded += len(texts)
            return httpx.Response(200, json={"vectors": [bag_of_words(text) for text in texts], "model": "x", "dim": DIM,
                                             "duration_ms": 1})
        return httpx.MockTransport(handle)


def publish(client, bus: InMemoryEventBus, event_type: str, payload: dict) -> None:
    """Событие доставляется в цикле событий приложения (как из RabbitMQ)."""
    client.portal.call(bus.publish, event_type, payload)
