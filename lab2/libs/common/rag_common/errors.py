"""Единый формат ошибок: {"error": {"code", "message", "request_id", "details"}}; stack trace клиенту не уходит."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from rag_common.logging import request_id_var

log = logging.getLogger("rag_common.errors")


class AppError(Exception):
    status_code = 500
    code = "internal_error"

    def __init__(self, message: str, *, code: str | None = None, status_code: int | None = None, details=None):
        super().__init__(message)
        self.message = message
        self.code = code or self.code
        self.status_code = status_code or self.status_code
        self.details = details


class BadRequest(AppError):
    status_code, code = 400, "bad_request"


class Unauthorized(AppError):
    status_code, code = 401, "unauthorized"


class Forbidden(AppError):
    status_code, code = 403, "forbidden"


class NotFound(AppError):
    status_code, code = 404, "not_found"


class Conflict(AppError):
    status_code, code = 409, "conflict"


class TooManyRequests(AppError):
    status_code, code = 429, "rate_limited"


class UpstreamError(AppError):
    """Внешний или соседний сервис ответил ошибкой или недоступен."""

    status_code, code = 502, "upstream_error"


class ServiceUnavailable(AppError):
    status_code, code = 503, "unavailable"


class UpstreamTimeout(AppError):
    status_code, code = 504, "upstream_timeout"


class ErrorBody(BaseModel):
    code: str
    message: str
    request_id: str | None = None
    details: list | dict | None = None


class ErrorResponse(BaseModel):
    """Схема ошибки для OpenAPI."""

    error: ErrorBody


def error_response(status_code: int, code: str, message: str, details=None, headers: dict | None = None) -> JSONResponse:
    body = {"code": code, "message": message, "request_id": request_id_var.get()}
    if details is not None:
        body["details"] = details
    return JSONResponse({"error": body}, status_code=status_code, headers=headers)


# Коды ответов для документации эндпоинтов: responses=error_docs(401, 404)
def error_docs(*codes: int) -> dict:
    return {code: {"model": ErrorResponse} for code in codes}


_HTTP_CODES = {400: "bad_request", 401: "unauthorized", 403: "forbidden", 404: "not_found", 405: "method_not_allowed"}


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error(_: Request, error: AppError):
        level = logging.WARNING if error.status_code < 500 else logging.ERROR
        log.log(level, "%s: %s", error.code, error.message, extra={"status": error.status_code})
        return error_response(error.status_code, error.code, error.message, error.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, error: RequestValidationError):
        details = [
            {"field": ".".join(str(part) for part in item["loc"] if part != "body"), "message": item["msg"]}
            for item in error.errors()
        ]
        log.warning("validation_error: %s", details, extra={"status": 422})
        return error_response(422, "validation_error", "Некорректные входные данные", details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, error: StarletteHTTPException):
        code = _HTTP_CODES.get(error.status_code, "http_error")
        return error_response(error.status_code, code, str(error.detail), headers=getattr(error, "headers", None))

    @app.exception_handler(SQLAlchemyError)
    async def database_error(_: Request, error: SQLAlchemyError):
        log.error("database_error", exc_info=error, extra={"status": 503})
        return error_response(503, "database_error", "База данных недоступна, повторите запрос позже")
