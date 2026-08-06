"""Trip planning use cases and ownership-safe orchestration."""

from collections.abc import Sequence
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.trips.models import Trip
from src.trips.repository import TripRepository
from src.trips.schemas import TripCreate, TripUpdate


class TripNotFoundError(Exception):
    """Raised when a trip is absent or is not owned by the caller."""


def _validate_date_range(start_date: date, end_date: date) -> None:
    """Validate a date range after merging a partial update with persisted data."""

    if end_date < start_date:
        raise ValueError("end_date must be on or after start_date")


async def create_trip(session: AsyncSession, user: User, request: TripCreate) -> Trip:
    """Create a trip for the authenticated user."""

    repository = TripRepository(session)
    return await repository.create(user.id, request.model_dump())


async def list_trips(
    session: AsyncSession,
    user: User,
    *,
    offset: int,
    limit: int,
) -> Sequence[Trip]:
    """List only trips owned by the authenticated user."""

    return await TripRepository(session).list_for_user(user.id, offset=offset, limit=limit)


async def get_trip(session: AsyncSession, user: User, trip_id: UUID) -> Trip:
    """Return an owned trip or raise a non-disclosing not-found error."""

    trip = await TripRepository(session).get_for_user(trip_id, user.id)
    if trip is None:
        raise TripNotFoundError
    return trip


async def update_trip(
    session: AsyncSession,
    user: User,
    trip_id: UUID,
    request: TripUpdate,
) -> Trip:
    """Apply a validated partial update to an owned trip."""

    repository = TripRepository(session)
    trip = await repository.get_for_user(trip_id, user.id)
    if trip is None:
        raise TripNotFoundError

    values = request.model_dump(exclude_unset=True)
    _validate_date_range(
        values.get("start_date", trip.start_date),
        values.get("end_date", trip.end_date),
    )
    return await repository.update(trip, values)


async def delete_trip(session: AsyncSession, user: User, trip_id: UUID) -> None:
    """Delete an owned trip or raise a non-disclosing not-found error."""

    repository = TripRepository(session)
    trip = await repository.get_for_user(trip_id, user.id)
    if trip is None:
        raise TripNotFoundError
    await repository.delete(trip)
