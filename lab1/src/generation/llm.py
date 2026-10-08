"""Клиент локальной LLM через HTTP API Ollama (/api/chat)."""

import re
from dataclasses import dataclass

import requests

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


class LLMError(Exception):
    """LLM недоступна или вернула ошибку."""


@dataclass
class LLMResponse:
    text: str
    model: str
    thinking: str = ""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    seconds: float = 0.0


class OllamaClient:
    def __init__(
        self,
        base_url: str,
        model: str,
        temperature: float = 0.1,
        num_ctx: int = 8192,
        think: bool | None = None,  # режим рассуждений qwen3; None — не передавать (модели без thinking)
        seed: int | None = 42,  # фиксированный seed: воспроизводимость экспериментов
        timeout_s: float = 180,
        session: requests.Session | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.options = {"temperature": temperature, "num_ctx": num_ctx}
        if seed is not None:
            self.options["seed"] = seed
        self.think = think
        self.timeout_s = timeout_s
        self.session = session or requests.Session()

    def chat(self, system: str, user: str, schema: dict | None = None) -> LLMResponse:
        """schema — JSON Schema ответа (structured output Ollama), например для LLM-судьи."""
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "stream": False,
            "options": self.options,
        }
        if self.think is not None:
            payload["think"] = self.think
        if schema is not None:
            payload["format"] = schema
        try:
            response = self.session.post(f"{self.base_url}/api/chat", json=payload, timeout=self.timeout_s)
        except requests.Timeout as error:
            raise LLMError(f"Ollama не ответила за {self.timeout_s} с") from error
        except requests.RequestException as error:
            raise LLMError(f"Ollama недоступна по адресу {self.base_url}: запустите Ollama") from error

        if response.status_code == 404:
            raise LLMError(f"модель {self.model} не скачана: выполните `ollama pull {self.model}`")
        if response.status_code != 200:
            raise LLMError(f"Ollama вернула {response.status_code}: {_error_text(response)}")

        data = response.json()
        message = data.get("message", {})
        return LLMResponse(
            text=_THINK_BLOCK.sub("", message.get("content", "")).strip(),  # на случай <think> в тексте
            model=self.model,
            thinking=message.get("thinking", ""),
            prompt_tokens=data.get("prompt_eval_count", 0),
            completion_tokens=data.get("eval_count", 0),
            seconds=data.get("total_duration", 0) / 1e9,
        )


def _error_text(response: requests.Response) -> str:
    try:
        return response.json().get("error", response.text)
    except ValueError:
        return response.text[:200]
