"""Consistent JSON exception handlers for the API boundary."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.core.logger import get_error_logger


def _error_payload(
    request: Request,
    code: str,
    message: Any,
    *,
    details: Any | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "error": {
            "code": code,
            "message": message,
            "request_id": getattr(request.state, "request_id", None),
        }
    }
    if details is not None:
        payload["error"]["details"] = details
    return payload


async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
    """Render expected HTTP exceptions in the API error envelope."""

    if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        get_error_logger().error("HTTP exception: %s", exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(request, "http_error", exc.detail),
        headers=exc.headers,
    )


async def handle_validation_exception(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Render invalid client input without exposing internal details."""

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload(
            request,
            "validation_error",
            "Request validation failed",
            details=jsonable_encoder(exc.errors()),
        ),
    )


async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
    """Log unexpected failures and return a safe response."""

    get_error_logger().exception("Unhandled application exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload(request, "internal_error", "Internal server error"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all boundary exception handlers."""

    app.add_exception_handler(HTTPException, handle_http_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)
    app.add_exception_handler(Exception, handle_unexpected_exception)
