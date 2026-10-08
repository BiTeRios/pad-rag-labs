"""HTTP-клиент для вызова соседних сервисов: таймаут, X-Request-ID и перевод сбоев в понятные ошибки.

- нет ответа за timeout → 504 UpstreamTimeout;
- сервис недоступен или ответил 5xx → 502 UpstreamError;
- ответ 4xx (например, 404) → та же ошибка с тем же кодом и сообщением.
"""

import logging

import httpx

from rag_common.errors import AppError, UpstreamError, UpstreamTimeout
from rag_common.logging import request_id_var
from rag_common.middleware import REQUEST_ID_HEADER

log = logging.getLogger("rag_common.http")


class ServiceClient:
    def __init__(self, name: str, base_url: str, timeout_s: float, transport: httpx.AsyncBaseTransport | None = None):
        self.name = name
        self.timeout_s = timeout_s
        self._client = httpx.AsyncClient(base_url=base_url, timeout=timeout_s, transport=transport)

    async def request(self, method: str, path: str, *, json=None, params=None, headers: dict | None = None,
                      timeout_s: float | None = None):
        request_headers = dict(headers or {})
        if request_id := request_id_var.get():
            request_headers[REQUEST_ID_HEADER] = request_id
        timeout = timeout_s or self.timeout_s
        try:
            response = await self._client.request(
                method, path, json=json, params=params, headers=request_headers, timeout=timeout
            )
        except httpx.TimeoutException as error:
            raise UpstreamTimeout(f"{self.name}: нет ответа за {timeout:.0f} с") from error
        except httpx.HTTPError as error:
            raise UpstreamError(f"{self.name} недоступен ({type(error).__name__})") from error

        if response.status_code >= 500:
            log.warning("%s %s %s → %d", self.name, method, path, response.status_code)
            raise UpstreamError(f"{self.name} ответил ошибкой {response.status_code}", details=_error_of(response))
        if response.status_code >= 400:
            error = _error_of(response) or {}
            raise AppError(
                error.get("message") or f"{self.name}: {response.status_code}",
                code=error.get("code"), status_code=response.status_code, details=error.get("details"),
            )
        return response.json() if response.content else None

    async def get(self, path: str, **kwargs):
        return await self.request("GET", path, **kwargs)

    async def post(self, path: str, **kwargs):
        return await self.request("POST", path, **kwargs)

    async def check(self) -> None:
        """Проверка для /ready: сосед отвечает на /health."""
        await self.get("/health", timeout_s=2.0)

    async def close(self) -> None:
        await self._client.aclose()


def _error_of(response: httpx.Response) -> dict | None:
    try:
        return response.json().get("error")
    except (ValueError, AttributeError):
        return None
