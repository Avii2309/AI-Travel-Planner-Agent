"""Response duration middleware."""

from collections.abc import Awaitable, Callable
from time import perf_counter

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


class ResponseTimeMiddleware(BaseHTTPMiddleware):
    """Expose the request processing duration as a response header."""

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        started_at = perf_counter()
        response = await call_next(request)
        response.headers["X-Process-Time-Ms"] = f"{(perf_counter() - started_at) * 1000:.2f}"
        return response
