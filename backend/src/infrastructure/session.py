"""Async-session factory and FastAPI session dependency."""

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """Create sessions with explicit transaction control and no stale object state."""

    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)


async def get_db_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Provide one session per request and roll it back if request handling fails."""

    session_factory = cast(
        async_sessionmaker[AsyncSession],
        request.app.state.session_factory,
    )
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
