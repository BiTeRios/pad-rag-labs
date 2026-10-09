"""Трассировка в Langfuse: что происходило внутри RAG на каждом вопросе.

- Вопрос → trace `rag-ask`: retrieval (vector search → фильтры → reranker, сколько chunks осталось на
  каждом шаге и с какими score) и вызов LLM (промпт, ответ, модель, параметры, токены, время).
- Прогон evaluation → session: trace на вопрос, метрики retrieval и оценки судьи — scores.
  Набор вопросов — dataset в Langfuse, прогон — dataset run: прогоны экспериментов сравниваются в UI.

Сервер Langfuse — self-hosted (`langfuse/docker-compose.yml`). Ключи — только в `.env`.
Без ключей, без пакета langfuse или при `langfuse.enabled: false` Tracer пустой: код пайплайна тот же,
тесты и запуск без Langfuse работают как раньше.
"""

import logging
import os
from contextlib import ExitStack, contextmanager
from typing import Any

log = logging.getLogger(__name__)

_TRANSLIT = dict(zip(
    "абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
    [*"a b v g d e e zh z i y k l m n o p r s t u f h ts ch sh sch".split(), "", "y", "", "e", "yu", "ya"],
    strict=True,
))


class _NoopObservation:
    trace_id = None
    id = None

    def update(self, **_: Any) -> "_NoopObservation":
        return self

    def set_trace_io(self, **_: Any) -> "_NoopObservation":
        return self


_NOOP = _NoopObservation()


class Tracer:
    """Тонкая обёртка над клиентом Langfuse; без клиента все вызовы ничего не делают."""

    def __init__(self, client=None, propagate=None, base_url: str = "", preview_chars: int = 300,
                 experiments: bool = True):
        self.client = client
        self.propagate = propagate  # propagate_attributes из SDK; в тестах — заглушка
        self.base_url = base_url
        self.preview_chars = preview_chars
        self.experiments = experiments  # propagate принимает experiment= (привязка trace к experiment)

    @property
    def enabled(self) -> bool:
        return self.client is not None

    @contextmanager
    def observe(
        self,
        name: str,
        as_type: str = "span",
        *,
        trace_seed: str | None = None,
        session_id: str | None = None,
        trace_name: str | None = None,
        tags: list[str] | None = None,
        **fields: Any,
    ):
        """Наблюдение (span / generation / retriever …) внутри текущего trace или новый trace.

        trace_seed — одинаковый seed даёт один и тот же trace: так три прохода evaluation
        (retrieval → генерация → судья) попадают в один trace на вопрос.
        """
        if self.client is None:
            yield _NOOP
            return
        trace_context = {"trace_id": self.trace_id(trace_seed)} if trace_seed else None
        with ExitStack() as stack:
            observation = stack.enter_context(self.client.start_as_current_observation(
                name=name, as_type=as_type, trace_context=trace_context, **fields
            ))
            if session_id or trace_name or tags:
                stack.enter_context(self.propagate(session_id=session_id, trace_name=trace_name, tags=tags))
            yield observation

    def trace_id(self, seed: str) -> str | None:
        return self.client.create_trace_id(seed=seed) if self.client else None

    def score(self, name: str, value: float, *, trace_seed: str | None = None, session_id: str | None = None,
              comment: str | None = None, data_type: str = "NUMERIC") -> None:
        """Оценка trace (по seed) или всего прогона (session); None — не отправляется."""
        if self.client is None or value is None:
            return
        self.client.create_score(
            name=name, value=value, data_type=data_type, comment=comment,
            trace_id=self.trace_id(trace_seed) if trace_seed else None, session_id=session_id,
        )

    def trace_url(self, trace_id: str | None) -> str | None:
        return self.client.get_trace_url(trace_id=trace_id) if self.client and trace_id else None

    def chunks_preview(self, chunks: list[dict]) -> list[dict]:
        """Chunks для trace: заголовок, url, score и начало текста — без полного контекста."""
        return [
            {
                "rank": rank,
                "heading": chunk.get("heading"),
                "url": chunk.get("url"),
                "score": round(chunk["score"], 4) if "score" in chunk else None,
                "rerank_score": round(chunk["rerank_score"], 4) if "rerank_score" in chunk else None,
                "text": chunk.get("text", "")[: self.preview_chars],
            }
            for rank, chunk in enumerate(chunks, 1)
        ]

    def flush(self) -> None:
        if self.client is not None:
            self.client.flush()


def ascii_id(value: str) -> str:
    """session_id и имя trace в Langfuse — только ASCII: «E6/с_reranker» → «E6/s_reranker»."""
    translit = "".join(_TRANSLIT.get(char.lower(), char) for char in value)
    return translit.encode("ascii", "replace").decode().replace("?", "_")


_CLIENTS: dict[tuple, Tracer] = {}


def build_tracer(cfg: dict) -> Tracer:
    """Tracer из config (`langfuse.*`) и ключей LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY из .env."""
    settings = cfg.get("langfuse") or {}
    if not settings.get("enabled"):
        return Tracer()
    public_key, secret_key = os.getenv("LANGFUSE_PUBLIC_KEY"), os.getenv("LANGFUSE_SECRET_KEY")
    if not (public_key and secret_key):
        log.info("Langfuse: нет LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY в .env — трассировка выключена")
        return Tracer()
    key = (settings["base_url"], public_key)
    if key in _CLIENTS:  # один клиент на процесс: эксперименты вызывают evaluate() много раз
        return _CLIENTS[key]
    try:
        from langfuse import Langfuse, propagate_attributes
    except ImportError:
        log.warning("Langfuse: пакет langfuse не установлен (pip install -r requirements.txt) — трассировка выключена")
        return Tracer()
    try:  # та же функция с параметром experiment: так trace привязывает к experiment сам run_experiment SDK
        from langfuse._client.propagation import _propagate_attributes as propagate
        experiments = True
    except ImportError:
        propagate, experiments = propagate_attributes, False

    client = Langfuse(
        public_key=public_key,
        secret_key=secret_key,
        base_url=settings["base_url"],
        environment=settings["environment"],
        sample_rate=settings["sample_rate"],
        timeout=settings["timeout_s"],
    )
    try:
        reachable = client.auth_check()
    except Exception as error:  # сеть, DNS, отказ в соединении — причина в логе, пайплайн работает дальше
        log.debug("Langfuse auth_check: %s", error)
        reachable = False
    if not reachable:
        log.warning("Langfuse недоступен по адресу %s или ключи неверны — трассировка выключена. "
                    "Запуск: docker compose -f langfuse/docker-compose.yml up -d", settings["base_url"])
        client.shutdown()
        return Tracer()
    tracer = Tracer(client, propagate, settings["base_url"], settings["preview_chars"], experiments)
    _CLIENTS[key] = tracer
    return tracer
