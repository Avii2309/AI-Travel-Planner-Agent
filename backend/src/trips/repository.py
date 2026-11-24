"""Async data access implementation for user-owned trips."""

from collections.abc import Mapping, Sequence
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.logger import get_error_logger
from src.trips.models import Trip


class TripRepository:
    """Repository whose reads are always scoped to a single user."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, user_id: UUID, values: Mapping[str, Any]) -> Trip:
        """Persist a new trip owned by ``user_id``."""

        trip = Trip(user_id=user_id, **dict(values))
        self.session.add(trip)
        try:
            await self.session.commit()
            await self.session.refresh(trip)
            return trip
        except SQLAlchemyError:
            await self.session.rollback()
            get_error_logger().exception("Failed to create a trip for user_id=%s", user_id)
            raise

    async def list_for_user(
        self,
        user_id: UUID,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> Sequence[Trip]:
        """Return a bounded page of trips owned by ``user_id``."""

        result = await self.session.execute(
            select(Trip)
            .where(Trip.user_id == user_id)
            .order_by(Trip.start_date.asc(), Trip.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_for_user(self, trip_id: UUID, user_id: UUID) -> Trip | None:
        """Return a trip only when it belongs to ``user_id``."""

        return await self.session.scalar(
            select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
        )

    async def update(self, trip: Trip, values: Mapping[str, Any]) -> Trip:
        """Apply validated values to an owned trip and persist them."""

        trip_id = trip.id
        for key, value in values.items():
            setattr(trip, key, value)
        try:
            await self.session.commit()
            await self.session.refresh(trip)
            return trip
        except SQLAlchemyError:
            await self.session.rollback()
            get_error_logger().exception("Failed to update trip_id=%s", trip_id)
            raise

    async def delete(self, trip: Trip) -> None:
        """Permanently delete an owned trip."""

        await self.session.delete(trip)
        await self.session.commit()
