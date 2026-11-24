"""Itinerary generation use case orchestration."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.logger import get_application_logger, get_error_logger
from src.locations.providers import GooglePlacesProvider
from src.locations.schemas import VerifiedPlace
from src.locations.service import (
    find_verified_attractions,
    find_verified_restaurants,
    verify_destination,
)
from src.itinerary.prompts import build_itinerary_prompt
from src.itinerary.providers import BaseAIProvider
from src.itinerary.models import Itinerary
from src.itinerary.repository import ItineraryRepository
from src.itinerary.schemas import (
    GeneratedItinerary,
    InvalidItineraryResponseError,
    ItineraryListItem,
    ItineraryResponse,
    itinerary_response_schema,
    parse_itinerary_response,
)
from src.trips.service import validate_trip_dates


class ItineraryTripNotFoundError(Exception):
    """Raised when the trip is absent or not owned by the current user."""


class ItineraryNotFoundError(Exception):
    """Raised when an owned trip does not yet have a saved itinerary."""


class InvalidStoredItineraryError(Exception):
    """Raised when stored content no longer matches the itinerary contract."""


async def generate_itinerary(
    session: AsyncSession,
    user: User,
    trip_id: UUID,
    provider: BaseAIProvider,
    places_provider: GooglePlacesProvider,
    *,
    timezone_name: str,
    repository: ItineraryRepository | None = None,
) -> ItineraryResponse:
    """Generate a validated itinerary for one authenticated user's trip."""

    get_application_logger().info("Itinerary generation requested for trip_id=%s", trip_id)
    trip_repository = repository or ItineraryRepository(session)
    trip = await trip_repository.get_trip_for_user(trip_id, user.id)
    if trip is None:
        raise ItineraryTripNotFoundError

    validate_trip_dates(
        trip.start_date,
        trip.end_date,
        timezone_name=timezone_name,
    )
    duration = (trip.end_date - trip.start_date).days + 1
    destination = await verify_destination(trip.destination, places_provider)
    attractions = await find_verified_attractions(
        destination,
        places_provider,
        required_count=duration,
    )
    restaurants = await find_verified_restaurants(destination, places_provider)
    verified_places = [*attractions, *restaurants]
    prompt = build_itinerary_prompt(
        source=trip.source,
        destination=destination.name,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        travelers=trip.travelers,
        preferences=trip.preferences,
        verified_places=verified_places,
    )
    raw_response = await provider.generate_itinerary(prompt, itinerary_response_schema())

    try:
        generated = parse_itinerary_response(
            raw_response,
            trip_id=trip.id,
            generated_at=datetime.now(timezone.utc),
            expected_days=duration,
            verified_places=verified_places,
        )
        saved = await trip_repository.save_current(
            trip_id=trip.id,
            user_id=user.id,
            content={
                **generated.model_dump(
                    exclude={"trip_id", "generated_at", "verified_places"},
                    mode="json",
                ),
                "verified_places": [place.model_dump(mode="json") for place in verified_places],
            },
        )
        return _response_from_saved(saved, trip.id)
    except InvalidItineraryResponseError:
        get_error_logger().error("Itinerary AI response parsing failed for trip_id=%s", trip_id)
        raise


def _response_from_saved(itinerary: Itinerary, trip_id: UUID) -> ItineraryResponse:
    """Reconstruct the validated public contract from persisted JSON content."""

    try:
        stored = dict(itinerary.content)
        raw_places = stored.pop("verified_places", [])
        verified_places = [VerifiedPlace.model_validate(place) for place in raw_places]
        content = GeneratedItinerary.model_validate(stored)
    except Exception as error:
        get_error_logger().error("Stored itinerary content is invalid for trip_id=%s", trip_id)
        raise InvalidStoredItineraryError from error
    return ItineraryResponse(
        trip_id=trip_id,
        generated_at=itinerary.updated_at,
        verified_places=verified_places,
        **content.model_dump(),
    )


async def get_itinerary(
    session: AsyncSession,
    user: User,
    trip_id: UUID,
    *,
    repository: ItineraryRepository | None = None,
) -> ItineraryResponse:
    """Return the saved itinerary for an owned trip."""

    itinerary_repository = repository or ItineraryRepository(session)
    trip = await itinerary_repository.get_trip_for_user(trip_id, user.id)
    if trip is None:
        raise ItineraryTripNotFoundError
    itinerary = await itinerary_repository.get_for_trip(trip_id, user.id)
    if itinerary is None:
        raise ItineraryNotFoundError
    return _response_from_saved(itinerary, trip_id)


async def list_itineraries(
    session: AsyncSession,
    user: User,
    *,
    repository: ItineraryRepository | None = None,
) -> list[ItineraryListItem]:
    """List lightweight metadata for the authenticated user's saved itineraries."""

    records = await (repository or ItineraryRepository(session)).list_for_user(user.id)
    return [
        ItineraryListItem(
            trip_id=trip.id,
            destination=trip.destination,
            start_date=trip.start_date,
            end_date=trip.end_date,
            generated_at=itinerary.updated_at,
        )
        for itinerary, trip in records
    ]
