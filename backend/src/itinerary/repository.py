"""Persistence access for user-owned generated itineraries."""

from collections.abc import Sequence
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from src.itinerary.models import Itinerary
from src.core.logger import get_error_logger
from src.trips.models import Trip


class ItineraryRepository:
    """Fetch trips scoped to the authenticated owner for itinerary use cases."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_trip_for_user(self, trip_id: UUID, user_id: UUID) -> Trip | None:
        """Return the requested trip only when it is owned by ``user_id``."""

        return await self.session.scalar(
            select(Trip).where(Trip.id == trip_id, Trip.user_id == user_id)
        )

    async def save_current(
        self,
        *,
        trip_id: UUID,
        user_id: UUID,
        content: dict[str, Any],
    ) -> Itinerary:
        """Create or replace the one current itinerary for an owned trip."""

        itinerary = await self.get_for_trip(trip_id, user_id)
        if itinerary is None:
            itinerary = Itinerary(trip_id=trip_id, user_id=user_id, content=content)
            self.session.add(itinerary)
        else:
            itinerary.content = content
        try:
            await self.session.commit()
            await self.session.refresh(itinerary)
            return itinerary
        except SQLAlchemyError:
            await self.session.rollback()
            get_error_logger().exception("Failed to save itinerary for trip_id=%s", trip_id)
            raise

    async def get_for_trip(self, trip_id: UUID, user_id: UUID) -> Itinerary | None:
        """Return the current itinerary only when it belongs to the caller."""

        return await self.session.scalar(
            select(Itinerary).where(Itinerary.trip_id == trip_id, Itinerary.user_id == user_id)
        )

    async def list_for_user(self, user_id: UUID) -> Sequence[tuple[Itinerary, Trip]]:
        """Return persisted itineraries with their owned trip metadata."""

        result = await self.session.execute(
            select(Itinerary, Trip)
            .join(Trip, Trip.id == Itinerary.trip_id)
            .where(Itinerary.user_id == user_id, Trip.user_id == user_id)
            .order_by(Itinerary.updated_at.desc())
        )
        return result.all()
