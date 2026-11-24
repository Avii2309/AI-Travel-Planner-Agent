"""Unit tests for the itinerary generation service."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
import json
from types import SimpleNamespace
import unittest
from uuid import uuid4

from src.itinerary.service import (
    ItineraryNotFoundError,
    ItineraryTripNotFoundError,
    generate_itinerary,
    get_itinerary,
    list_itineraries,
)
from src.itinerary.schemas import InvalidItineraryResponseError
from src.locations.service import (
    InvalidLocationError,
    NoVerifiedAttractionsError,
    verify_destination,
)
from src.locations.providers import GooglePlacesUnavailableError
from src.itinerary.providers import AIProviderUnavailableError
from zoneinfo import ZoneInfo


class StubPlacesProvider:
    """Local Places-response fixture for orchestration tests only."""

    async def search_text(self, query: str, **kwargs: object) -> list[dict[str, object]]:
        if query.startswith("tourist attractions"):
            return [
                {
                    "id": "place-1",
                    "displayName": {"text": "Verified Test Attraction"},
                    "formattedAddress": "1 Sample Road",
                    "location": {"latitude": 26.9, "longitude": 75.8},
                    "types": ["tourist_attraction"],
                }
            ]
        if query.startswith("restaurants"):
            return [
                {
                    "id": "restaurant-1",
                    "displayName": {"text": "Verified Test Restaurant"},
                    "formattedAddress": "2 Sample Road",
                    "location": {"latitude": 26.9, "longitude": 75.8},
                    "types": ["restaurant"],
                }
            ]
        return [
            {
                "id": "destination-1",
                "displayName": {"text": "Verified Test City"},
                "formattedAddress": "Sample Region",
                "location": {"latitude": 26.9124, "longitude": 75.7873},
                "types": ["locality"],
            }
        ]


class StubRepository:
    """In-memory repository replacement for service tests."""

    def __init__(self, trip: object) -> None:
        self.trip = trip
        self.saved_content: dict[str, object] | None = None
        self.itinerary: object | None = None

    async def get_trip_for_user(self, trip_id: object, user_id: object) -> object:
        return self.trip

    async def save_current(self, *, trip_id: object, user_id: object, content: dict[str, object]) -> object:
        self.saved_content = content
        self.itinerary = SimpleNamespace(content=content, updated_at=datetime.now(timezone.utc))
        return self.itinerary

    async def get_for_trip(self, trip_id: object, user_id: object) -> object | None:
        return self.itinerary

    async def list_for_user(self, user_id: object) -> list[tuple[object, object]]:
        return [] if self.itinerary is None else [(self.itinerary, self.trip)]


class StubProvider:
    """Provider replacement that captures the service's request."""

    def __init__(self) -> None:
        self.prompt = ""
        self.response_schema: dict[str, object] = {}

    async def generate_itinerary(self, prompt: str, response_schema: dict[str, object]) -> str:
        self.prompt = prompt
        self.response_schema = response_schema
        return json.dumps(
            {
                "days": [
                    {
                        "day": 1,
                        "title": "Arrival",
                        "activities": [
                            {
                                "time": "10:00",
                                "title": "AI-generated label",
                                "description": "Visit this verified attraction.",
                                "location": "AI-generated address",
                                "estimated_cost": 10,
                                "place_id": "place-1",
                            }
                        ],
                        "sightseeing": ["place-1"],
                        "food": ["restaurant-1"],
                        "transport": "Taxi",
                        "estimated_cost": 50,
                        "travel_tips": ["Use sunscreen"],
                        "optional_activities": [],
                    }
                ],
                "summary": "A beach getaway.",
                "estimated_total_cost": 50,
                "packing_tips": ["Sandals"],
                "best_visiting_time": "Early morning",
            }
        )


class InvalidOutputProvider:
    """Provider replacement returning non-JSON content."""

    async def generate_itinerary(self, prompt: str, response_schema: dict[str, object]) -> str:
        return "not valid JSON"


class UnavailableAIProvider:
    async def generate_itinerary(self, prompt: str, response_schema: dict[str, object]) -> str:
        raise AIProviderUnavailableError("AI provider unavailable")


class EmptyPlacesProvider:
    async def search_text(self, query: str, **kwargs: object) -> list[dict[str, object]]:
        return []


class FailedPlacesProvider:
    async def search_text(self, query: str, **kwargs: object) -> list[dict[str, object]]:
        from src.locations.providers import GooglePlacesUnavailableError

        raise GooglePlacesUnavailableError("Provider unavailable")


class NoAttractionsProvider(StubPlacesProvider):
    async def search_text(self, query: str, **kwargs: object) -> list[dict[str, object]]:
        if query.startswith("tourist attractions"):
            return []
        return await super().search_text(query, **kwargs)


class ItineraryServiceTests(unittest.IsolatedAsyncioTestCase):
    """Verify orchestration against a mocked AI provider."""

    async def test_generates_validated_itinerary_for_owned_trip(self) -> None:
        start = datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=10)
        trip = SimpleNamespace(
            id=uuid4(),
            source="Mumbai",
            destination="Verified Test City",
            start_date=start,
            end_date=start,
            budget=Decimal("10000.00"),
            travelers=2,
            preferences={"pace": "relaxed"},
        )
        provider = StubProvider()
        repository = StubRepository(trip)

        result = await generate_itinerary(
            session=SimpleNamespace(),
            user=SimpleNamespace(id=uuid4()),
            trip_id=trip.id,
            provider=provider,
            places_provider=StubPlacesProvider(),
            timezone_name="Asia/Kolkata",
            repository=repository,
        )

        self.assertEqual(result.trip_id, trip.id)
        self.assertIsNotNone(repository.saved_content)
        self.assertIn("Destination: Verified Test City", provider.prompt)
        self.assertEqual(result.days[0].activities[0].title, "Verified Test Attraction")
        self.assertEqual(result.days[0].activities[0].location, "1 Sample Road")
        self.assertEqual(result.verified_places[0].place_id, "place-1")
        self.assertEqual(result.days[0].food, ["Verified Test Restaurant"])
        self.assertIn("properties", provider.response_schema)

    async def test_invalid_destination_and_places_failure_are_not_treated_alike(self) -> None:
        with self.assertRaises(InvalidLocationError):
            await verify_destination("XYZ Unknown City 12345", EmptyPlacesProvider())

        with self.assertRaises(GooglePlacesUnavailableError):
            await verify_destination("Known City", FailedPlacesProvider())

    async def test_google_failure_prevents_ai_generation_and_persistence(self) -> None:
        start = datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=10)
        trip = SimpleNamespace(
            id=uuid4(), source="Origin", destination="Verified Test City",
            start_date=start, end_date=start, budget=Decimal("1000.00"),
            travelers=1, preferences={},
        )
        provider = StubProvider()
        repository = StubRepository(trip)

        with self.assertRaises(GooglePlacesUnavailableError):
            await generate_itinerary(
                session=SimpleNamespace(),
                user=SimpleNamespace(id=uuid4()),
                trip_id=trip.id,
                provider=provider,
                places_provider=FailedPlacesProvider(),
                timezone_name="Asia/Kolkata",
                repository=repository,
            )

        self.assertEqual(provider.prompt, "")
        self.assertIsNone(repository.saved_content)

    async def test_invalid_destination_prevents_ai_generation_and_persistence(self) -> None:
        start = datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=10)
        trip = SimpleNamespace(
            id=uuid4(), source="Origin", destination="XYZ Unknown City 12345",
            start_date=start, end_date=start, budget=Decimal("1000.00"),
            travelers=1, preferences={},
        )
        provider = StubProvider()
        repository = StubRepository(trip)

        with self.assertRaises(InvalidLocationError):
            await generate_itinerary(
                session=SimpleNamespace(),
                user=SimpleNamespace(id=uuid4()),
                trip_id=trip.id,
                provider=provider,
                places_provider=EmptyPlacesProvider(),
                timezone_name="Asia/Kolkata",
                repository=repository,
            )

        self.assertEqual(provider.prompt, "")
        self.assertIsNone(repository.saved_content)

    async def test_gemini_failure_does_not_persist_an_itinerary(self) -> None:
        start = datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=10)
        trip = SimpleNamespace(
            id=uuid4(), source="Origin", destination="Verified Test City",
            start_date=start, end_date=start, budget=Decimal("1000.00"),
            travelers=1, preferences={},
        )
        repository = StubRepository(trip)

        with self.assertRaises(AIProviderUnavailableError):
            await generate_itinerary(
                session=SimpleNamespace(),
                user=SimpleNamespace(id=uuid4()),
                trip_id=trip.id,
                provider=UnavailableAIProvider(),
                places_provider=StubPlacesProvider(),
                timezone_name="Asia/Kolkata",
                repository=repository,
            )

        self.assertIsNone(repository.saved_content)

    async def test_insufficient_verified_attractions_prevents_ai_generation(self) -> None:
        start = datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=10)
        trip = SimpleNamespace(
            id=uuid4(), source="Origin", destination="Verified Test City",
            start_date=start, end_date=start, budget=Decimal("1000.00"),
            travelers=1, preferences={},
        )
        provider = StubProvider()
        repository = StubRepository(trip)

        with self.assertRaises(NoVerifiedAttractionsError):
            await generate_itinerary(
                session=SimpleNamespace(),
                user=SimpleNamespace(id=uuid4()),
                trip_id=trip.id,
                provider=provider,
                places_provider=NoAttractionsProvider(),
                timezone_name="Asia/Kolkata",
                repository=repository,
            )

        self.assertEqual(provider.prompt, "")
        self.assertIsNone(repository.saved_content)

    async def test_retrieves_and_lists_only_saved_itinerary_metadata(self) -> None:
        trip = SimpleNamespace(
            id=uuid4(),
            destination="Goa",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 10),
        )
        repository = StubRepository(trip)
        await repository.save_current(
            trip_id=trip.id,
            user_id=uuid4(),
            content={
                "days": [{"day": 1, "title": "Arrival", "activities": [], "sightseeing": [], "food": [], "transport": "Taxi", "estimated_cost": 0, "travel_tips": [], "optional_activities": []}],
                "summary": "A short trip.", "estimated_total_cost": 0, "packing_tips": [], "best_visiting_time": "Morning",
            },
        )
        user = SimpleNamespace(id=uuid4())

        result = await get_itinerary(SimpleNamespace(), user, trip.id, repository=repository)
        listing = await list_itineraries(SimpleNamespace(), user, repository=repository)

        self.assertEqual(result.trip_id, trip.id)
        self.assertEqual(listing[0].destination, "Goa")

    async def test_invalid_provider_output_is_not_persisted(self) -> None:
        start = datetime.now(ZoneInfo("Asia/Kolkata")).date() + timedelta(days=10)
        trip = SimpleNamespace(
            id=uuid4(), source="Mumbai", destination="Verified Test City", start_date=start,
            end_date=start, budget=Decimal("10000.00"), travelers=2, preferences={},
        )
        repository = StubRepository(trip)

        with self.assertRaises(InvalidItineraryResponseError):
            await generate_itinerary(
                session=SimpleNamespace(), user=SimpleNamespace(id=uuid4()), trip_id=trip.id,
                provider=InvalidOutputProvider(), places_provider=StubPlacesProvider(),
                timezone_name="Asia/Kolkata", repository=repository,
            )

        self.assertIsNone(repository.saved_content)

    async def test_missing_trip_or_itinerary_is_not_disclosed(self) -> None:
        repository = StubRepository(None)
        user = SimpleNamespace(id=uuid4())
        trip_id = uuid4()

        with self.assertRaises(ItineraryTripNotFoundError):
            await get_itinerary(SimpleNamespace(), user, trip_id, repository=repository)

        repository.trip = SimpleNamespace(id=trip_id)
        with self.assertRaises(ItineraryNotFoundError):
            await get_itinerary(SimpleNamespace(), user, trip_id, repository=repository)


if __name__ == "__main__":
    unittest.main()
