"""Authenticated HTTP API for AI itinerary generation."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from src.auth.security import CurrentUserDependency
from src.locations.providers import GooglePlacesQuotaExceededError, GooglePlacesUnavailableError
from src.locations.router import PlacesProviderDependency
from src.locations.service import InvalidLocationError, NoVerifiedAttractionsError
from src.itinerary.providers import (
    AIProviderExecutionError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
    BaseAIProvider,
    get_ai_provider,
)
from src.itinerary.schemas import InvalidItineraryResponseError, ItineraryListItem, ItineraryResponse
from src.itinerary.service import (
    InvalidStoredItineraryError,
    ItineraryNotFoundError,
    ItineraryTripNotFoundError,
    generate_itinerary,
    get_itinerary,
    list_itineraries,
)
from src.presentation.api.dependencies import DatabaseSessionDependency, SettingsDependency
from src.trips.service import TripDateValidationError

router = APIRouter(prefix="/trips", tags=["itineraries"])
list_router = APIRouter(prefix="/itineraries", tags=["itineraries"])
TripId = Annotated[
    UUID,
    Path(
        description="ID of a trip owned by the authenticated user",
        examples={"owned_trip": {"summary": "Owned trip", "value": "550e8400-e29b-41d4-a716-446655440000"}},
    ),
]


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
        200: {"description": "Validated itinerary containing Google Places-verified attractions"},
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
    places_provider: PlacesProviderDependency,
    settings: SettingsDependency,
) -> ItineraryResponse | JSONResponse:
    """Generate a structured itinerary for an owned trip."""

    try:
        return await generate_itinerary(
            session,
            current_user,
            trip_id,
            provider,
            places_provider,
            timezone_name=settings.application_timezone,
        )
    except ItineraryTripNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found.") from error
    except TripDateValidationError as error:
        code = "INVALID_DATE_RANGE" if "end date" in str(error) else "PAST_START_DATE"
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"success": False, "error": code, "message": str(error)},
        )
    except InvalidLocationError:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "INVALID_LOCATION",
                "message": "The entered destination could not be verified. Please enter a valid location.",
            },
        )
    except NoVerifiedAttractionsError:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "NO_VERIFIED_ATTRACTIONS",
                "message": "Not enough verified attractions were found for this trip. Try a shorter trip or another destination.",
            },
        )
    except GooglePlacesQuotaExceededError:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "success": False,
                "error": "GOOGLE_PLACES_QUOTA_EXCEEDED",
                "message": "Google Places request quota was exceeded. Please try again later.",
            },
        )
    except GooglePlacesUnavailableError as error:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "success": False,
                "error": "GOOGLE_PLACES_UNAVAILABLE",
                "message": f"{error} No itinerary was generated.",
            },
        )
    except AIProviderRateLimitError as error:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(error)) from error
    except AIProviderTimeoutError as error:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(error)) from error
    except AIProviderUnavailableError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except (AIProviderExecutionError, InvalidItineraryResponseError) as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(error)) from error
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "PERSISTENCE_ERROR",
                "message": "The itinerary could not be saved. Please try again.",
            },
        )


@router.get(
    "/{trip_id}/itinerary",
    response_model=ItineraryResponse,
    summary="Get a saved AI travel itinerary",
    responses={404: {"description": "Trip or itinerary does not exist or is not owned by the caller"}},
)
async def get_trip_itinerary(
    trip_id: TripId,
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
) -> ItineraryResponse:
    """Retrieve the current persisted itinerary for one owned trip."""

    try:
        return await get_itinerary(session, current_user, trip_id)
    except (ItineraryTripNotFoundError, ItineraryNotFoundError) as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Itinerary not found.") from error
    except InvalidStoredItineraryError as error:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Saved itinerary is unavailable.") from error


@list_router.get("", response_model=list[ItineraryListItem], summary="List my saved AI itineraries")
async def list_saved_itineraries(
    session: DatabaseSessionDependency,
    current_user: CurrentUserDependency,
) -> list[ItineraryListItem]:
    """Return metadata for itineraries accessible to the authenticated user."""

    return await list_itineraries(session, current_user)
