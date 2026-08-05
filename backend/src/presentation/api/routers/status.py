"""Versioned API status route."""

from fastapi import APIRouter

from src.presentation.api.dependencies import SettingsDependency

router = APIRouter(tags=["status"])


@router.get("/status", summary="Versioned API status")
async def api_status(settings: SettingsDependency) -> dict[str, str]:
    """Return the current versioned API status."""

    return {
        "status": "operational",
        "api_version": settings.api_v1_prefix.removeprefix("/"),
    }
