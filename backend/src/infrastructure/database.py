"""PostgreSQL async-engine configuration and connection diagnostics."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

from src.core.settings import AppSettings


def create_database_engine(settings: AppSettings) -> AsyncEngine:
    """Build the application's pooled SQLAlchemy async engine."""

    return create_async_engine(
        settings.database_url,
        echo=settings.debug,
        pool_pre_ping=True,
        pool_size=settings.database_pool_size,
        max_overflow=settings.database_max_overflow,
        pool_timeout=settings.database_pool_timeout,
        pool_recycle=settings.database_pool_recycle,
    )


async def check_database_connection(session: AsyncSession) -> None:
    """Raise a SQLAlchemy error when PostgreSQL cannot execute a trivial query."""

    await session.execute(text("SELECT 1"))
