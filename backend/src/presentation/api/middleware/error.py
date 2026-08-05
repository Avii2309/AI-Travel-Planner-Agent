"""Unexpected-error middleware."""

from collections.abc import Awaitable, Callable

from fastapi import Request
from fastapi.responses import JSONResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.logger import get_error_logger


class ErrorMiddleware(BaseHTTPMiddleware):
    """Log unhandled exceptions and return a safe JSON error response."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        try:
            return await call_next(request)
        except Exception:
            request_id = getattr(request.state, "request_id", None)
            get_error_logger().exception(
                "Unhandled request error: method=%s path=%s request_id=%s",
                request.method,
                request.url.path,
                request_id,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "request_id": request_id,
                },
            )
