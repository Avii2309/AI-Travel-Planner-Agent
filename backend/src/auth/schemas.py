"""Request and response contracts for authentication endpoints."""

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    """Validated registration input."""

    email: EmailStr
    full_name: Annotated[str, Field(min_length=1, max_length=255)]
    password: Annotated[str, Field(min_length=8, max_length=72)]

    @field_validator("full_name")
    @classmethod
    def normalize_full_name(cls, value: str) -> str:
        """Reject whitespace-only names and store a normalized value."""

        normalized_value = " ".join(value.split())
        if not normalized_value:
            raise ValueError("full_name must contain non-whitespace characters")
        return normalized_value

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        """Keep passwords within bcrypt's 72-byte input limit."""

        if len(value.encode("utf-8")) > 72:
            raise ValueError("password must not exceed 72 UTF-8 bytes")
        return value


class LoginRequest(BaseModel):
    """Credentials used to request an access token."""

    email: EmailStr
    password: Annotated[str, Field(min_length=1, max_length=72)]

    @field_validator("password")
    @classmethod
    def validate_bcrypt_password_length(cls, value: str) -> str:
        """Keep login validation consistent with registration."""

        if len(value.encode("utf-8")) > 72:
            raise ValueError("password must not exceed 72 UTF-8 bytes")
        return value


class AccessTokenResponse(BaseModel):
    """Bearer token returned after a successful login."""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserResponse(BaseModel):
    """Safe user fields exposed by authentication endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    full_name: str
    created_at: datetime
