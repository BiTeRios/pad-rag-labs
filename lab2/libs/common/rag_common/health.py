"""GET /health — процесс жив (liveness); GET /ready — зависимости доступны (readiness).

Проверки готовности сервис кладёт в app.state.ready_checks: {"database": async fn, ...}.
Функция проверки бросает исключение, если зависимость недоступна.
"""

import asyncio
from collections.abc import Awaitable, Callable

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

ReadyCheck = Callable[[], Awaitable[object]]
CHECK_TIMEOUT_S = 3.0  # проба readiness не должна висеть дольше таймаута Kubernetes

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness: процесс жив")
async def health(request: Request) -> dict:
    return {"status": "ok", "service": request.app.state.settings.service_name}


@router.get("/ready", summary="Readiness: зависимости доступны", responses={503: {"description": "не готов"}})
async def ready(request: Request) -> JSONResponse:
    checks: dict[str, ReadyCheck] = getattr(request.app.state, "ready_checks", {})
    results = await asyncio.gather(*(_run(check) for check in checks.values()))
    report = dict(zip(checks, results, strict=True))
    ok = all(result == "ok" for result in results)
    return JSONResponse(
        {"status": "ready" if ok else "not_ready", "service": request.app.state.settings.service_name, "checks": report},
        status_code=200 if ok else 503,
    )


async def _run(check: ReadyCheck) -> str:
    try:
        await asyncio.wait_for(check(), CHECK_TIMEOUT_S)
        return "ok"
    except TimeoutError:
        return f"error: нет ответа за {CHECK_TIMEOUT_S:.0f} с"
    except Exception as error:  # noqa: BLE001 — любая ошибка зависимости = не готов
        return f"error: {type(error).__name__}: {error}"[:200]
