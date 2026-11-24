"""Google Places-backed location verification and attraction discovery."""

from math import asin, cos, radians, sin, sqrt
import re

from src.locations.providers import GooglePlacesProvider, parse_verified_place
from src.locations.schemas import VerifiedPlace

LOCAL_PLACES_SEARCH_RADIUS_METERS = 25_000


class InvalidLocationError(Exception):
    """Raised only when Google Places returned no verifiable destination."""


class NoVerifiedAttractionsError(Exception):
    """Raised when Google Places returned too few nearby attractions."""


_GENERIC_LOCATION_WORDS = {
    "at",
    "city",
    "cities",
    "country",
    "county",
    "district",
    "in",
    "near",
    "of",
    "region",
    "state",
    "the",
    "town",
}


def _location_tokens(value: str) -> set[str]:
    return {
        token
        for token in re.findall(r"[\w]+", value.casefold())
        if token not in _GENERIC_LOCATION_WORDS
    }


async def verify_destination(query: str, provider: GooglePlacesProvider) -> VerifiedPlace:
    """Resolve a user-entered destination to Google's canonical place record."""

    results = await provider.search_text(query)
    query_tokens = _location_tokens(query)
    if not query_tokens:
        raise InvalidLocationError
    for result in results:
        place = parse_verified_place(result)
        if place is not None:
            place_tokens = _location_tokens(f"{place.name} {place.formatted_address}")
            matches = len(query_tokens & place_tokens)
            numeric_tokens = {token for token in query_tokens if token.isdigit()}
            minimum_matches = min(2, len(query_tokens))
            if matches >= minimum_matches and numeric_tokens <= place_tokens:
                return place
    raise InvalidLocationError


def _distance_km(first: VerifiedPlace, second: VerifiedPlace) -> float:
    """Calculate great-circle distance for filtering out distant search results."""

    latitude_delta = radians(second.latitude - first.latitude)
    longitude_delta = radians(second.longitude - first.longitude)
    value = (
        sin(latitude_delta / 2) ** 2
        + cos(radians(first.latitude))
        * cos(radians(second.latitude))
        * sin(longitude_delta / 2) ** 2
    )
    return 6371 * 2 * asin(sqrt(value))


async def _find_verified_places(
    destination: VerifiedPlace,
    provider: GooglePlacesProvider,
    *,
    query: str,
    place_type: str,
    required_count: int,
) -> list[VerifiedPlace]:
    """Return unique Google places of the requested type inside the destination area."""

    results = await provider.search_text(
        query,
        center=(destination.latitude, destination.longitude),
        radius_meters=LOCAL_PLACES_SEARCH_RADIUS_METERS,
        included_type=place_type,
    )
    places: list[VerifiedPlace] = []
    seen_ids = {destination.place_id}
    for result in results:
        place = parse_verified_place(result)
        if (
            place is None
            or place.place_id in seen_ids
            or place_type not in place.types
            or _distance_km(destination, place) > LOCAL_PLACES_SEARCH_RADIUS_METERS / 1000
        ):
            continue
        places.append(place)
        seen_ids.add(place.place_id)

    places.sort(key=lambda place: _distance_km(destination, place))
    if len(places) < required_count:
        if place_type == "tourist_attraction":
            raise NoVerifiedAttractionsError
        return []
    return places


async def find_verified_attractions(
    destination: VerifiedPlace,
    provider: GooglePlacesProvider,
    *,
    required_count: int,
) -> list[VerifiedPlace]:
    """Return nearby verified attractions, requiring enough for the trip duration."""

    return await _find_verified_places(
        destination,
        provider,
        query=f"tourist attractions in {destination.name}",
        place_type="tourist_attraction",
        required_count=required_count,
    )


async def find_verified_restaurants(
    destination: VerifiedPlace,
    provider: GooglePlacesProvider,
) -> list[VerifiedPlace]:
    """Return nearby verified restaurants; an empty list is allowed."""

    return await _find_verified_places(
        destination,
        provider,
        query=f"restaurants in {destination.name}",
        place_type="restaurant",
        required_count=0,
    )
