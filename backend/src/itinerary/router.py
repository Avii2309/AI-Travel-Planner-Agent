"""Authenticated HTTP API for AI itinerary generation."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status

from src.auth.security import CurrentUserDependency
from src.itinerary.providers import (
    AIProviderExecutionError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    BaseAIProvider,
    get_ai_provider,
)
from src.itinerary.schemas import InvalidItineraryResponseError, ItineraryResponse
from src.itinerary.service import ItineraryTripNotFoundError, generate_itinerary
from src.presentation.api.dependencies import DatabaseSessionDependency, SettingsDependency

router = APIRouter(prefix="/trips", tags=["itineraries"])
TripId = Annotated[
    UUID,
    Path(
        description="ID of a trip owned by the authenticated user",
        examples={"owned_trip": {"summary": "Owned trip", "value": "550e8400-e29b-41d4-a716-446655440000"}},
    ),
]

_ITINERARY_RESPONSE_EXAMPLE = {
    "trip_id": "550e8400-e29b-41d4-a716-446655440000",
    "generated_at": "2026-08-07T10:30:00Z",
    "days": [
        {
            "day": 1,
            "title": "Arrival and historic centre",
            "activities": [
                {
                    "time": "10:00-12:00",
                    "title": "Old Town walk",
                    "description": "Explore the central landmarks at an easy pace.",
                    "location": "Old Town",
                    "estimated_cost": 15.0,
                }
            ],
            "sightseeing": ["Old Town"],
            "food": ["Try a local lunch near the main square"],
            "transport": "Use the airport train and walk within the centre.",
            "estimated_cost": 65.0,
            "travel_tips": ["Carry a refillable water bottle."],
            "optional_activities": ["Sunset viewpoint"],
        }
    ],
    "summary": "A relaxed city break with a mix of landmarks and local food.",
    "estimated_total_cost": 65.0,
    "packing_tips": ["Comfortable walking shoes", "Light rain jacket"],
    "best_visiting_time": "Early morning for major sights and sunset for viewpoints.",
}


def get_itinerary_provider(settings: SettingsDependency) -> BaseAIProvider:
    """Resolve the configured provider through the existing settings dependency."""

    return get_ai_provider(settings)


ItineraryProviderDependency = Annotated[BaseAIProvider, Depends(get_itinerary_provider)]


@router.post(
    "/{trip_id}/generate-itinerary",
    response_model=ItineraryResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate an AI travel itinerary",
    description=(
        "Generates an itinerary from the saved trip details. No request body is required; "
        "send a Bearer token for the trip owner."
    ),
    responses={
        200: {"description": "Validated itinerary", "content": {"application/json": {"example": _ITINERARY_RESPONSE_EXAMPLE}}},
        404: {"description": "Trip does not exist or is not owned by the caller"},
        429: {"description": "AI provider rate limit reached"},
        502: {"description": "AI provider returned an invalid response"},
        503: {"description": "AI provider is not configured or unavailable"},
        504: {"description": "AI provider timed out"},
    },
)
async def generate_trip_itinerary(
    trip_id: TripId,
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
    provider: ItineraryProviderDependency,
) -> ItineraryResponse:
    """Generate a structured itinerary for an owned trip."""

    try:
        return await generate_itinerary(session, current_user, trip_id, provider)
    except ItineraryTripNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.") from error
    except AIProviderRateLimitError as error:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(error)) from error
    except AIProviderTimeoutError as error:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(error)) from error
    except AIProviderUnavailableError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except (AIProviderExecutionError, InvalidItineraryResponseError) as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
