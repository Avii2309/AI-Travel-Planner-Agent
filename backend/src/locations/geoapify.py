"""Geoapify forward-geocoding client and result resolution."""

from collections.abc import Mapping
from math import isfinite
import re
from typing import Any

import httpx

from src.core.settings import AppSettings
from src.locations.schemas import VerifiedGeocodedLocation

GEOAPIFY_FORWARD_GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
_GEOGRAPHIC_RESULT_TYPES = {
    "amenity",
    "building",
    "city",
    "county",
    "country",
    "district",
    "locality",
    "municipality",
    "neighbourhood",
    "neighborhood",
    "postcode",
    "quarter",
    "state",
    "street",
    "suburb",
    "town",
    "village",
}
_GENERIC_WORDS = {"at", "city", "in", "of", "the", "town"}


class GeoapifyError(Exception):
    """Base class for Geoapify request failures."""


class GeoapifyConfigurationError(GeoapifyError):
    """Raised when Geoapify is not configured."""


class GeoapifyUnavailableError(GeoapifyError):
    """Raised when Geoapify cannot provide a reliable response."""


class GeoapifyProvider:
    """Small async client for Geoapify forward geocoding."""

    def __init__(self, settings: AppSettings) -> None:
        key = settings.geoapify_api_key
        self.api_key = key.get_secret_value().strip() if key else None
        self.timeout_seconds = settings.geoapify_timeout_seconds

    async def geocode(self, query: str) -> list[Mapping[str, Any]]:
        """Return Geoapify results without exposing credentials or provider details."""

        if not self.api_key:
            raise GeoapifyConfigurationError

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(
                    GEOAPIFY_FORWARD_GEOCODING_URL,
                    params={
                        "text": query,
                        "format": "json",
                        "limit": 5,
                        "apiKey": self.api_key,
                    },
                )
        except httpx.TimeoutException as error:
            raise GeoapifyUnavailableError from error
        except httpx.RequestError as error:
            raise GeoapifyUnavailableError from error

        if response.is_error:
            raise GeoapifyUnavailableError
        try:
            payload = response.json()
        except ValueError as error:
            raise GeoapifyUnavailableError from error
        results = payload.get("results") if isinstance(payload, dict) else None
        if not isinstance(results, list):
            raise GeoapifyUnavailableError
        return [result for result in results if isinstance(result, dict)]


def _tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\w]+", value.casefold())
        if token not in _GENERIC_WORDS
    }


def _parse_geocoded_location(raw: Mapping[str, Any]) -> VerifiedGeocodedLocation | None:
    result_type = raw.get("result_type")
    name = raw.get("name")
    if not isinstance(name, str) or not name.strip():
        name = next(
            (
                raw.get(field)
                for field in ("city", "locality", "district", "state", "country")
                if isinstance(raw.get(field), str) and raw[field].strip()
            ),
            None,
        )
    formatted = raw.get("formatted")
    latitude = raw.get("lat")
    longitude = raw.get("lon")
    place_id = raw.get("place_id")
    if (
        not isinstance(result_type, str)
        or result_type.casefold() not in _GEOGRAPHIC_RESULT_TYPES
        or not isinstance(name, str)
        or not name.strip()
        or not isinstance(formatted, str)
        or not formatted.strip()
        or not isinstance(latitude, (int, float))
        or not isinstance(longitude, (int, float))
        or not isfinite(latitude)
        or not isfinite(longitude)
    ):
        return None
    try:
        return VerifiedGeocodedLocation(
            place_id=place_id if isinstance(place_id, str) and place_id.strip() else None,
            name=name.strip(),
            formatted_address=formatted.strip(),
            latitude=float(latitude),
            longitude=float(longitude),
        )
    except ValueError:
        return None


def resolve_geocoded_location(
    query: str,
    results: list[Mapping[str, Any]],
) -> tuple[VerifiedGeocodedLocation | None, bool]:
    """Resolve only a single suitable result matching every meaningful query token."""

    query_tokens = _tokens(query)
    if not query_tokens:
        return None, False

    matches: list[VerifiedGeocodedLocation] = []
    seen: set[tuple[object, ...]] = set()
    for result in results:
        location = _parse_geocoded_location(result)
        if location is None:
            continue
        result_tokens = _tokens(
            " ".join(
                str(result.get(field, ""))
                for field in (
                    "name",
                    "formatted",
                    "city",
                    "locality",
                    "district",
                    "state",
                    "country",
                    "postcode",
                )
            )
        )
        if not query_tokens.issubset(result_tokens):
            continue
        identity = (
            location.place_id
            if location.place_id
            else (round(location.latitude, 4), round(location.longitude, 4))
        )
        if identity not in seen:
            seen.add(identity)
            matches.append(location)

    if len(matches) == 1:
        return matches[0], False
    return None, len(matches) > 1
