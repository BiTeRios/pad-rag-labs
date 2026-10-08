"""Проксирование запросов к сервисам: маршрут → JWT → роли → rate limit → сервис."""

import asyncio
import logging

import httpx
from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html

from gateway_service.routing import find_route
from rag_common.auth import USER_ID_HEADER, USER_ROLE_HEADER, Identity, decode_token
from rag_common.errors import AppError, Forbidden, NotFound, Unauthorized, UpstreamError, UpstreamTimeout, error_response
from rag_common.logging import request_id_var
from rag_common.middleware import REQUEST_ID_HEADER

log = logging.getLogger(__name__)

router = APIRouter()

HOP_BY_HOP = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization", "te", "trailers",
              "transfer-encoding", "upgrade", "host", "content-length"}
# Заголовки личности ставит только gateway: присланные клиентом удаляются (иначе их можно подделать)
# X-Request-ID и X-Forwarded-For gateway ставит сам (он — граница системы), поэтому входящие тоже убираются
STRIPPED_REQUEST = HOP_BY_HOP | {USER_ID_HEADER.lower(), USER_ROLE_HEADER.lower(), "authorization",
                                 REQUEST_ID_HEADER.lower(), "x-forwarded-for"}
DOCUMENTED_SERVICES = ("auth", "ingestion", "indexing", "retrieval", "chat", "analytics")
METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE"]


def _identity(request: Request, required: bool) -> Identity | None:
    settings = request.app.state.settings
    header = request.headers.get("authorization", "")
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        if required:
            raise Unauthorized("Нужен заголовок Authorization: Bearer <token> (POST /api/auth/login)")
        return None
    try:
        return decode_token(token, secret=settings.jwt_secret, algorithm=settings.jwt_algorithm, issuer=settings.jwt_issuer)
    except AppError:
        if required:
            raise
        return None  # публичный маршрут (например, login) с просроченным токеном — как без токена


async def proxy(request: Request, path: str) -> Response:
    state, settings = request.app.state, request.app.state.settings
    route = find_route(state.routes, request.url.path)
    if route is None:
        raise NotFound(f"Маршрут {request.url.path} не найден")
    identity = _identity(request, required=route.auth == "required")
    if route.roles and (identity is None or identity.role not in route.roles):
        raise Forbidden(f"Недостаточно прав: нужна роль {' или '.join(route.roles)}")

    client_ip = request.client.host if request.client else "unknown"
    limit = route.rate_limit_per_minute or settings.rate_limit_per_minute
    bucket = f"{identity.user_id if identity else client_ip}:{route.prefix if route.rate_limit_per_minute else '*'}"
    if (retry_after := state.limiter.check(bucket, limit)) is not None:
        log.warning("Превышен лимит запросов", extra={"bucket": bucket, "limit_per_minute": limit})
        return error_response(429, "rate_limited", f"Не больше {limit} запросов в минуту, повторите через {retry_after} с",
                              headers={"Retry-After": str(retry_after)})

    body = await request.body()
    if len(body) > settings.max_body_bytes:
        return error_response(413, "payload_too_large", f"Тело запроса больше {settings.max_body_bytes} байт")
    headers = {key: value for key, value in request.headers.items() if key.lower() not in STRIPPED_REQUEST}
    headers[REQUEST_ID_HEADER] = request_id_var.get()
    headers["X-Forwarded-For"] = client_ip
    if identity:
        headers.update(identity.headers())

    timeout = route.timeout_s or settings.upstream_timeout_s
    url = state.service_urls[route.service].rstrip("/") + request.url.path
    try:
        upstream = await state.http.request(request.method, url, params=request.query_params, content=body,
                                            headers=headers, timeout=timeout)
    except httpx.TimeoutException as error:
        raise UpstreamTimeout(f"{route.service}-service: нет ответа за {timeout:.0f} с") from error
    except httpx.HTTPError as error:
        raise UpstreamError(f"{route.service}-service недоступен") from error

    log.info("→ %s %d", route.service, upstream.status_code,
             extra={"service_route": route.service, "upstream_status": upstream.status_code,
                    "user_id": identity.user_id if identity else None})
    response_headers = {k: v for k, v in upstream.headers.items() if k.lower() not in HOP_BY_HOP | {"content-encoding"}}
    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers)


@router.get("/api/status", tags=["gateway"], summary="Готовность всех сервисов (агрегация /ready)")
async def status(request: Request) -> JSONResponse:
    state = request.app.state

    async def ready(name: str, url: str) -> tuple[str, str]:
        try:
            response = await state.http.get(f"{url.rstrip('/')}/ready", timeout=3.0)
            return name, "ready" if response.status_code == 200 else "not_ready"
        except httpx.HTTPError:
            return name, "unreachable"

    results = dict(await asyncio.gather(*(ready(name, url) for name, url in state.service_urls.items())))
    overall = "ok" if all(value == "ready" for value in results.values()) else "degraded"
    return JSONResponse({"status": overall, "services": results}, status_code=200 if overall == "ok" else 503)


@router.get("/docs/{service}", tags=["gateway"], summary="Swagger UI сервиса через gateway", response_class=HTMLResponse)
async def service_docs(service: str) -> HTMLResponse:
    if service not in DOCUMENTED_SERVICES:
        raise NotFound(f"Документация есть для: {', '.join(DOCUMENTED_SERVICES)}")
    return get_swagger_ui_html(openapi_url=f"/openapi/{service}.json", title=f"{service}-service через gateway")


@router.get("/openapi/{service}.json", tags=["gateway"], summary="OpenAPI сервиса, адаптированная для вызова через gateway")
async def service_openapi(service: str, request: Request) -> JSONResponse:
    if service not in DOCUMENTED_SERVICES:
        raise NotFound("Нет такого сервиса")
    url = request.app.state.service_urls[service].rstrip("/") + "/openapi.json"
    try:
        spec = (await request.app.state.http.get(url, timeout=5.0)).json()
    except (httpx.HTTPError, ValueError) as error:
        raise UpstreamError(f"{service}-service недоступен") from error
    return JSONResponse(for_gateway(spec))


def for_gateway(spec: dict) -> dict:
    """Через gateway: без /internal и проб, авторизация — Bearer, заголовки личности скрыты (их ставит gateway)."""
    hidden = {USER_ID_HEADER, USER_ROLE_HEADER}
    paths = {}
    for path, operations in spec.get("paths", {}).items():
        if not path.startswith("/api/"):
            continue
        for operation in operations.values():
            operation["parameters"] = [p for p in operation.get("parameters", []) if p.get("name") not in hidden]
        paths[path] = operations
    spec["paths"] = paths
    spec["servers"] = [{"url": "/"}]
    spec.setdefault("components", {})["securitySchemes"] = {"bearer": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}}
    spec["security"] = [{"bearer": []}]
    return spec


# Catch-all регистрируется последним: иначе он перехватил бы /api/status
router.add_api_route("/api/{path:path}", proxy, methods=METHODS, include_in_schema=False)
