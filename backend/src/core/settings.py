"""Typed application settings loaded from the environment and .env files."""

from enum import Enum
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPOSITORY_ROOT / "backend"


class Environment(str, Enum):
    """Supported deployment environments."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"
    TESTING = "testing"


class EnvironmentSelector(BaseSettings):
    """Loads only the environment before selecting an environment profile."""

    model_config = SettingsConfigDict(
        env_file=(REPOSITORY_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias="APP_ENV",
    )


class AppSettings(BaseSettings):
    """Common settings shared by all application environments."""

    model_config = SettingsConfigDict(
        env_file=(REPOSITORY_ROOT / ".env", BACKEND_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "AI Travel Planner API"
    app_version: str = "0.1.0"
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        validation_alias="APP_ENV",
    )
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["http://localhost:3000"]
    log_level: str = "INFO"
    log_directory: Path = REPOSITORY_ROOT / "logs"
    docs_enabled: bool = True

    @field_validator("log_directory", mode="before")
    @classmethod
    def resolve_log_directory(cls, value: str | Path) -> Path:
        """Resolve relative log locations from the repository root."""

        path = Path(value)
        return path if path.is_absolute() else REPOSITORY_ROOT / path


class DevelopmentSettings(AppSettings):
    """Developer-friendly defaults."""

    debug: bool = True
    log_level: str = "DEBUG"


class ProductionSettings(AppSettings):
    """Safe production defaults."""

    debug: bool = False
    docs_enabled: bool = False


class TestingSettings(AppSettings):
    """Deterministic defaults for automated tests."""

    debug: bool = False
    log_level: str = "WARNING"
    docs_enabled: bool = False


@lru_cache
def get_settings() -> AppSettings:
    """Return the cached profile selected by APP_ENV."""

    environment = EnvironmentSelector().environment
    profiles: dict[Environment, type[AppSettings]] = {
        Environment.DEVELOPMENT: DevelopmentSettings,
        Environment.PRODUCTION: ProductionSettings,
        Environment.TESTING: TestingSettings,
    }
    return profiles[environment]()
