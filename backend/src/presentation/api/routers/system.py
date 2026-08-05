"""Unauthenticated service discovery and health routes."""

from fastapi import APIRouter

from src.presentation.api.dependencies import SettingsDependency

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
async def health_check() -> dict[str, str]:
    """Confirm that the API process is available."""

    return {"status": "healthy"}
