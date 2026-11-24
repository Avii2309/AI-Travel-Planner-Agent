"""Trip planning use cases and ownership-safe orchestration."""

from collections.abc import Sequence
from datetime import date, datetime
from zoneinfo import ZoneInfo
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.locations.geoapify import (
    GeoapifyConfigurationError,
    GeoapifyProvider,
    GeoapifyUnavailableError,
    resolve_geocoded_location,
)
from src.locations.schemas import VerifiedGeocodedLocation
from src.trips.models import Trip
from src.trips.repository import TripRepository
from src.trips.schemas import TripCreate, TripUpdate


class TripNotFoundError(Exception):
    """Raised when a trip is absent or is not owned by the caller."""


class TripDateValidationError(Exception):
    """Raised when a trip date range violates application date rules."""

    def __init__(self, code: str, field: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.field = field


def validate_trip_dates(
    start_date: date,
    end_date: date,
    *,
    timezone_name: str,
    today: date | None = None,
) -> None:
    """Require a non-past start date and a same-day-or-later end date."""

    application_today = today or datetime.now(ZoneInfo(timezone_name)).date()
    if start_date < application_today:
        raise TripDateValidationError(
            "PAST_START_DATE",
            "start_date",
            "Trip start date cannot be in the past. Please select today or a future date.",
        )
    if end_date < start_date:
        raise TripDateValidationError(
            "INVALID_DATE_RANGE",
            "end_date",
            "End date cannot be earlier than the start date.",
        )


class TripLocationValidationError(Exception):
    """Raised when Geoapify cannot resolve a location unambiguously."""

    def __init__(self, code: str, field: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.field = field


class TripLocationServiceError(Exception):
    """Raised when Geoapify is unconfigured or unavailable."""

    def __init__(self, code: str, field: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.field = field


async def _verify_trip_location(
    query: str,
    provider: GeoapifyProvider,
    *,
    field: str,
    label: str,
) -> VerifiedGeocodedLocation:
    try:
        results = await provider.geocode(query)
    except GeoapifyConfigurationError as error:
        raise TripLocationServiceError(
            "LOCATION_VERIFICATION_NOT_CONFIGURED",
            field,
            "Location verification service is not configured.",
        ) from error
    except GeoapifyUnavailableError as error:
        raise TripLocationServiceError(
            "LOCATION_VERIFICATION_UNAVAILABLE",
            field,
            "Location verification service is temporarily unavailable. Please try again.",
        ) from error

    location, ambiguous = resolve_geocoded_location(query, results)
    if ambiguous:
        raise TripLocationValidationError(
            f"AMBIGUOUS_{'START' if field == 'start_location' else 'DESTINATION'}",
            field,
            f"{label} is ambiguous. Please enter a more specific location.",
        )
    if location is None:
        code = "INVALID_START_LOCATION" if field == "start_location" else "INVALID_DESTINATION"
        raise TripLocationValidationError(
            code,
            field,
            f"{label} could not be verified. Please enter a valid {label.lower()}.",
        )
    return location


async def create_trip(
    session: AsyncSession,
    user: User,
    request: TripCreate,
    *,
    geoapify_provider: GeoapifyProvider,
    timezone_name: str,
) -> Trip:
    """Create a trip for the authenticated user."""

    validate_trip_dates(request.start_date, request.end_date, timezone_name=timezone_name)
    source = await _verify_trip_location(
        request.source,
        geoapify_provider,
        field="start_location",
        label="Starting location",
    )
    destination = await _verify_trip_location(
        request.destination,
        geoapify_provider,
        field="destination",
        label="Destination",
    )
    values = request.model_dump()
    values.update(
        source_place_id=source.place_id,
        source_name=source.name,
        source_address=source.formatted_address,
        source_latitude=source.latitude,
        source_longitude=source.longitude,
        destination_place_id=destination.place_id,
        destination_name=destination.name,
        destination_address=destination.formatted_address,
        destination_latitude=destination.latitude,
        destination_longitude=destination.longitude,
    )
    repository = TripRepository(session)
    return await repository.create(user.id, values)


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
    *,
    geoapify_provider: GeoapifyProvider,
    timezone_name: str,
) -> Trip:
    """Apply a validated partial update to an owned trip."""

    repository = TripRepository(session)
    trip = await repository.get_for_user(trip_id, user.id)
    if trip is None:
        raise TripNotFoundError

    values = request.model_dump(exclude_unset=True)
    validate_trip_dates(
        values.get("start_date", trip.start_date),
        values.get("end_date", trip.end_date),
        timezone_name=timezone_name,
    )
    if "source" in values:
        location = await _verify_trip_location(
            values["source"],
            geoapify_provider,
            field="start_location",
            label="Starting location",
        )
        values.update(
            source_place_id=location.place_id,
            source_name=location.name,
            source_address=location.formatted_address,
            source_latitude=location.latitude,
            source_longitude=location.longitude,
        )
    if "destination" in values:
        location = await _verify_trip_location(
            values["destination"],
            geoapify_provider,
            field="destination",
            label="Destination",
        )
        values.update(
            destination_place_id=location.place_id,
            destination_name=location.name,
            destination_address=location.formatted_address,
            destination_latitude=location.latitude,
            destination_longitude=location.longitude,
        )
    return await repository.update(trip, values)


async def delete_trip(session: AsyncSession, user: User, trip_id: UUID) -> None:
    """Delete an owned trip or raise a non-disclosing not-found error."""

    repository = TripRepository(session)
    trip = await repository.get_for_user(trip_id, user.id)
    if trip is None:
        raise TripNotFoundError
    await repository.delete(trip)
