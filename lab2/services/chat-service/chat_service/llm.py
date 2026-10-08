"""Клиент Ollama (/api/chat), асинхронный. Из Lab1 (src/generation/llm.py); сбои → 502/504 с понятной причиной."""

import re
from dataclasses import dataclass

import httpx

from rag_common.errors import UpstreamError, UpstreamTimeout

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0


class OllamaClient:
    def __init__(self, base_url: str, model: str, *, temperature: float, num_ctx: int, think: bool | None,
                 seed: int | None, timeout_s: float, transport: httpx.AsyncBaseTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.options = {"temperature": temperature, "num_ctx": num_ctx}
        if seed is not None:
            self.options["seed"] = seed
        self.think = think
        self.timeout_s = timeout_s
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout_s, transport=transport)

    async def chat(self, system: str, user: str) -> LLMResponse:
        payload = {
            "model": self.model, "stream": False, "options": self.options,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        }
        if self.think is not None:
            payload["think"] = self.think
        try:
            response = await self._client.post("/api/chat", json=payload)
        except httpx.TimeoutException as error:
            raise UpstreamTimeout(f"LLM ({self.model}) не ответила за {self.timeout_s:.0f} с", code="llm_timeout") from error
        except httpx.HTTPError as error:
            raise UpstreamError(f"LLM недоступна по адресу {self.base_url}: запущена ли Ollama?", code="llm_unavailable") from error
        if response.status_code == 404:
            raise UpstreamError(f"Модель {self.model} не скачана в Ollama: ollama pull {self.model}", code="llm_model_missing")
        if response.status_code != 200:
            raise UpstreamError(f"LLM вернула {response.status_code}", code="llm_error")
        data = response.json()
        return LLMResponse(
            text=_THINK_BLOCK.sub("", data.get("message", {}).get("content", "")).strip(),
            model=self.model,
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            seconds=round(data.get("total_duration", 0) / 1e9, 2),
        )

    async def check(self) -> None:
        """Для /ready: Ollama отвечает, и нужная модель скачана."""
        response = await self._client.get("/api/tags", timeout=2.0)
        names = {model["name"] for model in response.json().get("models", [])}
        if self.model not in names and f"{self.model}:latest" not in names:
            raise RuntimeError(f"модель {self.model} не скачана")

    async def close(self) -> None:
        await self._client.aclose()
