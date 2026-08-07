"""Unit tests for the itinerary generation service."""

from datetime import date
from decimal import Decimal
import json
from types import SimpleNamespace
import unittest
from uuid import uuid4

from src.itinerary.service import generate_itinerary


class StubRepository:
    """In-memory repository replacement for service tests."""

    def __init__(self, trip: object) -> None:
        self.trip = trip

    async def get_trip_for_user(self, trip_id: object, user_id: object) -> object:
        return self.trip


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
                        "activities": [],
                        "sightseeing": ["Beach"],
                        "food": ["Seafood"],
                        "transport": "Taxi",
                        "estimated_cost": 50,
                        "travel_tips": ["Use sunscreen"],
                        "optional_activities": ["Boat ride"],
                    }
                ],
                "summary": "A beach getaway.",
                "estimated_total_cost": 50,
                "packing_tips": ["Sandals"],
                "best_visiting_time": "Early morning",
            }
        )


class ItineraryServiceTests(unittest.IsolatedAsyncioTestCase):
    """Verify orchestration against a mocked AI provider."""

    async def test_generates_validated_itinerary_for_owned_trip(self) -> None:
        trip = SimpleNamespace(
            id=uuid4(),
            source="Mumbai",
            destination="Goa",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 10),
            budget=Decimal("10000.00"),
            travelers=2,
            preferences={"pace": "relaxed"},
        )
        provider = StubProvider()

        result = await generate_itinerary(
            session=SimpleNamespace(),
            user=SimpleNamespace(id=uuid4()),
            trip_id=trip.id,
            provider=provider,
            repository=StubRepository(trip),
        )

        self.assertEqual(result.trip_id, trip.id)
        self.assertIn("Destination: Goa", provider.prompt)
        self.assertIn("properties", provider.response_schema)


if __name__ == "__main__":
    unittest.main()
