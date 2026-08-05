"""Password hashing, JWT primitives, and current-user dependency."""

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.settings import AppSettings
from src.presentation.api.dependencies import DatabaseSessionDependency, SettingsDependency

PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")
BEARER_SCHEME = HTTPBearer(auto_error=False, scheme_name="JWTBearer")


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""

    return PASSWORD_CONTEXT.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Return whether a plaintext password matches its bcrypt hash."""

    return PASSWORD_CONTEXT.verify(password, hashed_password)


def create_access_token(user_id: UUID, settings: AppSettings) -> str:
    """Create a signed, expiring JWT access token for a user."""

    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "type": "access",
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def _authentication_exception() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )


def _decode_access_token(token: str, settings: AppSettings) -> UUID:
    """Validate an access token and return its user identifier."""

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
        if payload.get("type") != "access":
            raise ValueError("Unexpected token type")
        return UUID(str(payload["sub"]))
    except (JWTError, KeyError, TypeError, ValueError) as error:
        raise _authentication_exception() from error


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(BEARER_SCHEME)],
    session: DatabaseSessionDependency,
    settings: SettingsDependency,
) -> User:
    """Resolve a valid Bearer token to its current database user."""

    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _authentication_exception()

    user_id = _decode_access_token(credentials.credentials, settings)
    user = await session.scalar(select(User).where(User.id == user_id))
    if user is None:
        raise _authentication_exception()
    return user


CurrentUserDependency = Annotated[User, Depends(get_current_user)]
