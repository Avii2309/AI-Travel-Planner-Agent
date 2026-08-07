"""Read-only persistence access for itinerary generation."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
