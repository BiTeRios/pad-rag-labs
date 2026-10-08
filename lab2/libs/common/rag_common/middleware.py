"""Request ID и журнал запросов.

X-Request-ID берётся из входящего запроса (его ставит gateway) или создаётся; он попадает во все логи
обработки запроса, в исходящие вызовы соседних сервисов и в события брокера.
"""

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from rag_common.errors import error_response
from rag_common.logging import request_id_var

REQUEST_ID_HEADER = "X-Request-ID"
QUIET_PATHS = ("/health", "/ready")  # пробы Kubernetes раз в несколько секунд — не засоряют журнал

log = logging.getLogger("rag_common.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex
        token = request_id_var.set(request_id)
        started = time.perf_counter()
        try:
            try:
                response = await call_next(request)
            except Exception:  # непойманная ошибка: в лог — со stack trace, клиенту — общий ответ
                log.exception("unhandled_error", extra={"method": request.method, "path": request.url.path})
                response = error_response(500, "internal_error", "Внутренняя ошибка сервиса")
            response.headers[REQUEST_ID_HEADER] = request_id
            if request.url.path not in QUIET_PATHS:
                log.info(
                    "%s %s → %d", request.method, request.url.path, response.status_code,
                    extra={
                        "method": request.method, "path": request.url.path, "status": response.status_code,
                        "duration_ms": round((time.perf_counter() - started) * 1000, 1),
                    },
                )
            return response
        finally:
            request_id_var.reset(token)
