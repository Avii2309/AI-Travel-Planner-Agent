"""Google Places API integration and provider-level error translation."""

from collections.abc import Mapping
from typing import Any

import httpx

from src.core.settings import AppSettings
from src.locations.schemas import VerifiedPlace

PLACES_TEXT_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACES_FIELD_MASK = (
    "places.id,places.displayName,places.formattedAddress,"
    "places.location,places.types"
)


class GooglePlacesError(Exception):
    """Base class for failures contacting Google Places."""


class GooglePlacesQuotaExceededError(GooglePlacesError):
    """Google Places rejected a request because its quota was exhausted."""


class GooglePlacesUnavailableError(GooglePlacesError):
    """Google Places is unconfigured or unavailable."""


class GooglePlacesAuthenticationError(GooglePlacesUnavailableError):
    """Google Places rejected the API key or its API restrictions."""


class GooglePlacesBillingError(GooglePlacesUnavailableError):
    """Google Places requires billing to be enabled for the Cloud project."""


class GooglePlacesProvider:
    """Small async client for Google Places API (New) text search."""

    def __init__(self, settings: AppSettings) -> None:
        api_key = settings.effective_google_places_api_key
        self.api_key = api_key.get_secret_value().strip() if api_key else None
        self.timeout_seconds = settings.google_places_timeout_seconds

    async def search_text(
        self,
        query: str,
        *,
        center: tuple[float, float] | None = None,
        radius_meters: float | None = None,
        included_type: str | None = None,
    ) -> list[Mapping[str, Any]]:
        """Search Places with server-held credentials and a bounded timeout."""

        if not self.api_key:
            raise GooglePlacesUnavailableError(
                "Google Places is not configured. Set GOOGLE_PLACES_API_KEY or "
                "GOOGLE_MAPS_API_KEY in the backend environment."
            )

        payload: dict[str, Any] = {"textQuery": query, "maxResultCount": 20}
        if center is not None and radius_meters is not None:
            latitude, longitude = center
            payload["locationBias"] = {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": radius_meters,
                }
            }
        if included_type:
            payload["includedType"] = included_type
            payload["strictTypeFiltering"] = True

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    PLACES_TEXT_SEARCH_URL,
                    headers={
                        "Content-Type": "application/json",
                        "X-Goog-Api-Key": self.api_key,
                        "X-Goog-FieldMask": PLACES_FIELD_MASK,
                    },
                    json=payload,
                )
        except httpx.TimeoutException as error:
            raise GooglePlacesUnavailableError("Google Places request timed out.") from error
        except httpx.RequestError as error:
            raise GooglePlacesUnavailableError("Google Places is temporarily unavailable.") from error

        if response.status_code == 429:
            raise GooglePlacesQuotaExceededError("Google Places request quota was exceeded.")

        try:
            result = response.json()
        except ValueError as error:
            raise GooglePlacesUnavailableError("Google Places returned an unreadable response.") from error

        if response.is_error or (isinstance(result, dict) and "error" in result):
            details = result.get("error", {}) if isinstance(result, dict) else {}
            google_status = details.get("status") if isinstance(details, dict) else None
            google_message = details.get("message", "") if isinstance(details, dict) else ""
            message_lower = google_message.casefold() if isinstance(google_message, str) else ""
            if (
                google_status == "RESOURCE_EXHAUSTED"
                or "quota" in message_lower
                or "rate limit" in message_lower
            ):
                raise GooglePlacesQuotaExceededError("Google Places request quota was exceeded.")
            if "billing" in message_lower or "billingNotEnabled".casefold() in message_lower:
                raise GooglePlacesBillingError(
                    "Google Maps Platform billing is not enabled for this project."
                )
            if response.status_code in {401, 403} or google_status in {
                "UNAUTHENTICATED",
                "PERMISSION_DENIED",
            }:
                raise GooglePlacesAuthenticationError(
                    "Google Places rejected the API key or access. Check that the key is valid, "
                    "Places API (New) is enabled, and key restrictions allow this server."
                )
            if isinstance(google_message, str) and google_message:
                raise GooglePlacesUnavailableError(
                    f"Google Places request failed: {google_message}"
                )
            raise GooglePlacesUnavailableError(
                "Google Places is temporarily unavailable. Check Google Cloud API status and billing."
            )

        if not isinstance(result, dict):
            raise GooglePlacesUnavailableError("Google Places returned an invalid response.")
        places = result.get("places", [])
        if not isinstance(places, list):
            raise GooglePlacesUnavailableError("Google Places returned an invalid response.")
        return [place for place in places if isinstance(place, dict)]


def parse_verified_place(raw: Mapping[str, Any]) -> VerifiedPlace | None:
    """Convert a Google Place record only when its identity and coordinates are complete."""

    display_name = raw.get("displayName")
    coordinates = raw.get("location")
    if not isinstance(display_name, dict) or not isinstance(coordinates, dict):
        return None
    name = display_name.get("text")
    place_id = raw.get("id")
    address = raw.get("formattedAddress")
    latitude = coordinates.get("latitude")
    longitude = coordinates.get("longitude")
    if (
        not isinstance(name, str)
        or not name.strip()
        or not isinstance(place_id, str)
        or not place_id.strip()
        or not isinstance(address, str)
        or not address.strip()
        or not isinstance(latitude, (int, float))
        or not isinstance(longitude, (int, float))
    ):
        return None
    raw_types = raw.get("types", [])
    types = [item for item in raw_types if isinstance(item, str)] if isinstance(raw_types, list) else []
    try:
        return VerifiedPlace(
            place_id=place_id,
            name=name,
            formatted_address=address,
            latitude=float(latitude),
            longitude=float(longitude),
            types=types,
        )
    except ValueError:
        return None
