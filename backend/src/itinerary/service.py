"""Itinerary generation use case orchestration."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.models import User
from src.core.logger import get_application_logger, get_error_logger
from src.itinerary.prompts import build_itinerary_prompt
from src.itinerary.providers import BaseAIProvider
from src.itinerary.repository import ItineraryRepository
from src.itinerary.schemas import (
    InvalidItineraryResponseError,
    ItineraryResponse,
    itinerary_response_schema,
    parse_itinerary_response,
)


class ItineraryTripNotFoundError(Exception):
    """Raised when the trip is absent or not owned by the current user."""


async def generate_itinerary(
    session: AsyncSession,
    user: User,
    trip_id: UUID,
    provider: BaseAIProvider,
    *,
    repository: ItineraryRepository | None = None,
) -> ItineraryResponse:
    """Generate a validated itinerary for one authenticated user's trip."""

    get_application_logger().info("Itinerary generation requested for trip_id=%s", trip_id)
    trip_repository = repository or ItineraryRepository(session)
    trip = await trip_repository.get_trip_for_user(trip_id, user.id)
    if trip is None:
        raise ItineraryTripNotFoundError

    prompt = build_itinerary_prompt(
        source=trip.source,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        budget=trip.budget,
        travelers=trip.travelers,
        preferences=trip.preferences,
    )
    raw_response = await provider.generate_itinerary(prompt, itinerary_response_schema())

    try:
        return parse_itinerary_response(
            raw_response,
            trip_id=trip.id,
            generated_at=datetime.now(timezone.utc),
            expected_days=(trip.end_date - trip.start_date).days + 1,
        )
    except InvalidItineraryResponseError:
        get_error_logger().error("Itinerary AI response parsing failed for trip_id=%s", trip_id)
        raise
