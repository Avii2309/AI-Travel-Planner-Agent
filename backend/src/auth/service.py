"""Application service for registration and credential authentication."""

from fastapi.concurrency import run_in_threadpool
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.auth.schemas import RegisterRequest
from src.auth.security import hash_password, verify_password


class EmailAlreadyRegisteredError(Exception):
    """Raised when registration would violate the unique email invariant."""


class InvalidCredentialsError(Exception):
    """Raised when supplied credentials cannot authenticate a user."""


def normalize_email(email: str) -> str:
    """Normalize email addresses so the unique database value is case-insensitive."""

    return email.strip().casefold()


async def register_user(session: AsyncSession, request: RegisterRequest) -> User:
    """Create a user after enforcing the email uniqueness constraint."""

    email = normalize_email(str(request.email))
    existing_user = await session.scalar(
        select(User.id).where(func.lower(User.email) == email).limit(1)
    )
    if existing_user is not None:
        raise EmailAlreadyRegisteredError

    user = User(
        email=email,
        full_name=request.full_name,
        hashed_password=await run_in_threadpool(hash_password, request.password),
    )
    session.add(user)
    try:
        await session.commit()
    except IntegrityError as error:
        await session.rollback()
        raise EmailAlreadyRegisteredError from error
    await session.refresh(user)
    return user


async def authenticate_user(session: AsyncSession, email: str, password: str) -> User:
    """Validate credentials without revealing whether the email exists."""

    user = await session.scalar(
        select(User).where(func.lower(User.email) == normalize_email(email)).limit(1)
    )
    if user is None or not await run_in_threadpool(
        verify_password,
        password,
        user.hashed_password,
    ):
        raise InvalidCredentialsError
    return user
