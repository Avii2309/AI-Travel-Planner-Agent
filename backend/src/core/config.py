"""FastAPI application factory and registration point."""

from fastapi import FastAPI

from src.core.settings import AppSettings
from src.presentation.api.exceptions.handlers import register_exception_handlers
from src.presentation.api.middleware.registration import register_middleware
from src.presentation.api.routers.status import router as status_router
from src.presentation.api.routers.system import router as system_router


def create_application(settings: AppSettings) -> FastAPI:
    """Create and fully configure the FastAPI application."""

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
    )
    app.state.settings = settings

    register_exception_handlers(app)
    register_middleware(app, settings)
    app.include_router(system_router)
    app.include_router(status_router, prefix=settings.api_v1_prefix)

    return app
