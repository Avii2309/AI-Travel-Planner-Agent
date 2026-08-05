"""FastAPI dependency providers."""

from typing import Annotated, cast

from fastapi import Depends, Request

from src.core.settings import AppSettings


def get_app_settings(request: Request) -> AppSettings:
    """Provide the settings instance attached during application creation."""

    return cast(AppSettings, request.app.state.settings)


SettingsDependency = Annotated[AppSettings, Depends(get_app_settings)]
