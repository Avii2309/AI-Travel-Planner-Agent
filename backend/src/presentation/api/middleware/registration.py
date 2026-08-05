"""Middleware registration in the intended execution order."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.settings import AppSettings
from src.presentation.api.middleware.error import ErrorMiddleware
from src.presentation.api.middleware.request_logging import RequestLoggingMiddleware
from src.presentation.api.middleware.response_time import ResponseTimeMiddleware


def register_middleware(app: FastAPI, settings: AppSettings) -> None:
    """Register error handling, observability, timing, and browser CORS support."""

    app.add_middleware(ErrorMiddleware)
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(ResponseTimeMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
