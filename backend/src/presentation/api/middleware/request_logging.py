"""Request lifecycle logging middleware."""

from collections.abc import Awaitable, Callable
from time import perf_counter
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from src.core.logger import get_request_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Attach a request ID and write one log record per request."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        request.state.request_id = request_id
        started_at = perf_counter()

        try:
            response = await call_next(request)
        except Exception:
            get_request_logger().exception(
                "request_failed method=%s path=%s request_id=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                request_id,
                (perf_counter() - started_at) * 1000,
            )
            raise

        duration_ms = (perf_counter() - started_at) * 1000
        response.headers["X-Request-ID"] = request_id
        get_request_logger().info(
            "request_complete method=%s path=%s status_code=%s request_id=%s duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
            duration_ms,
        )
        return response
