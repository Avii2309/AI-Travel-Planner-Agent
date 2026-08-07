"""Unit tests for AI itinerary response parsing."""

from datetime import datetime, timezone
import json
import unittest
from uuid import uuid4

from src.itinerary.schemas import InvalidItineraryResponseError, parse_itinerary_response


def _response(day: int = 1) -> str:
    return json.dumps(
        {
            "days": [
                {
                    "day": day,
                    "title": "Arrival",
                    "activities": [
                        {
                            "time": "10:00",
                            "title": "Walk",
                            "description": "Explore nearby sights.",
                            "location": "Centre",
                            "estimated_cost": 10,
                        }
                    ],
                    "sightseeing": ["Centre"],
                    "food": ["Local cafe"],
                    "transport": "Walk",
                    "estimated_cost": 20,
                    "travel_tips": ["Wear sunscreen"],
                    "optional_activities": ["Museum"],
                }
            ],
            "summary": "A short trip.",
            "estimated_total_cost": 20,
            "packing_tips": ["Shoes"],
            "best_visiting_time": "Morning",
        }
    )


class ItineraryResponseParserTests(unittest.TestCase):
    """Verify only complete, duration-aligned AI responses are accepted."""

    def test_parses_valid_response_and_adds_metadata(self) -> None:
        trip_id = uuid4()
        generated_at = datetime.now(timezone.utc)

        result = parse_itinerary_response(
            _response(),
            trip_id=trip_id,
            generated_at=generated_at,
            expected_days=1,
        )

        self.assertEqual(result.trip_id, trip_id)
        self.assertEqual(result.generated_at, generated_at)
        self.assertEqual(result.days[0].day, 1)

    def test_rejects_mismatched_day_numbers(self) -> None:
        with self.assertRaises(InvalidItineraryResponseError):
            parse_itinerary_response(
                _response(day=2),
                trip_id=uuid4(),
                generated_at=datetime.now(timezone.utc),
                expected_days=1,
            )


if __name__ == "__main__":
    unittest.main()
