"""Authenticated endpoint for explicit destination verification."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.auth.security import CurrentUserDependency
from src.core.settings import AppSettings
from src.locations.providers import (
    GooglePlacesProvider,
    GooglePlacesQuotaExceededError,
    GooglePlacesUnavailableError,
)
from src.locations.geoapify import GeoapifyProvider
from src.locations.schemas import LocationVerificationResponse
from src.locations.service import InvalidLocationError, verify_destination
from src.presentation.api.dependencies import SettingsDependency

router = APIRouter(prefix="/locations", tags=["locations"])


class LocationVerificationRequest(BaseModel):
    """A destination string to resolve against Google Places."""

    destination: str = Field(min_length=1, max_length=255)


def get_places_provider(settings: SettingsDependency) -> GooglePlacesProvider:
    """Construct the Google Places API provider."""

    return GooglePlacesProvider(settings)


PlacesProviderDependency = Annotated[GooglePlacesProvider, Depends(get_places_provider)]


def get_geoapify_provider(settings: SettingsDependency) -> GeoapifyProvider:
    """Construct the Geoapify provider with a server-side API key."""

    return GeoapifyProvider(settings)


GeoapifyProviderDependency = Annotated[GeoapifyProvider, Depends(get_geoapify_provider)]


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": code, "message": message},
    )


@router.post(
    "/verify",
    response_model=LocationVerificationResponse,
    summary="Verify a destination with Google Places",
)
async def verify_location(
    request: LocationVerificationRequest,
    _current_user: CurrentUserDependency,
    provider: PlacesProviderDependency,
) -> LocationVerificationResponse | JSONResponse:
    """Verify a destination without relying on AI-generated geography."""

    destination = " ".join(request.destination.split())
    if not destination:
        return _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "INVALID_LOCATION",
            "The entered destination could not be verified. Please enter a valid location.",
        )
    try:
        place = await verify_destination(destination, provider)
    except InvalidLocationError:
        return _error(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "INVALID_LOCATION",
            "The entered destination could not be verified. Please enter a valid location.",
        )
    except GooglePlacesQuotaExceededError:
        return _error(
            status.HTTP_429_TOO_MANY_REQUESTS,
            "GOOGLE_PLACES_QUOTA_EXCEEDED",
            "Google Places request quota was exceeded. Please try again later.",
        )
    except GooglePlacesUnavailableError as error:
        return _error(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "GOOGLE_PLACES_UNAVAILABLE",
            str(error),
        )
    return LocationVerificationResponse(
        place_id=place.place_id,
        name=place.name,
        formatted_address=place.formatted_address,
        latitude=place.latitude,
        longitude=place.longitude,
        types=place.types,
    )
