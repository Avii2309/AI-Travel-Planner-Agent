"""Unauthenticated service discovery and health routes."""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from src.infrastructure.database import check_database_connection
from src.presentation.api.dependencies import DatabaseSessionDependency, SettingsDependency

router = APIRouter(tags=["system"])


@router.get("/", summary="Service information")
async def root(settings: SettingsDependency) -> dict[str, str]:
    """Return basic API identity information."""

    return {
        "message": f"Welcome to {settings.app_name}",
        "environment": settings.environment.value,
        "version": settings.app_version,
    }


@router.get("/health", summary="Health check")
async def health_check(session: DatabaseSessionDependency) -> dict[str, str]:
    """Confirm that the API process and PostgreSQL connection are available."""

    try:
        await check_database_connection(session)
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database is unavailable.",
        ) from error

    return {"status": "healthy", "database": "connected"}
