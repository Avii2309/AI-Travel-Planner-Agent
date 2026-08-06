"""FastAPI application factory and registration point."""

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from src.core.settings import AppSettings
from src.auth.router import router as auth_router
from src.infrastructure.database import create_database_engine
from src.infrastructure.session import create_session_factory
from src.presentation.api.exceptions.handlers import register_exception_handlers
from src.presentation.api.middleware.registration import register_middleware
from src.presentation.api.routers.status import router as status_router
from src.presentation.api.routers.system import router as system_router
from src.trips.router import router as trips_router


def create_application(settings: AppSettings) -> FastAPI:
    """Create and fully configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """Create and dispose shared database resources with the application."""

        engine = create_database_engine(settings)
        app.state.database_engine = engine
        app.state.session_factory = create_session_factory(engine)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs" if settings.docs_enabled else None,
        redoc_url="/redoc" if settings.docs_enabled else None,
        openapi_url="/openapi.json" if settings.docs_enabled else None,
        lifespan=lifespan,
    )
    app.state.settings = settings

    register_exception_handlers(app)
    register_middleware(app, settings)
    app.include_router(system_router)
    app.include_router(status_router, prefix=settings.api_v1_prefix)
    app.include_router(auth_router)
    app.include_router(trips_router)

    return app
