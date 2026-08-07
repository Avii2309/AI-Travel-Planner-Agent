"""Unit tests for itinerary prompt construction."""

from datetime import date
from decimal import Decimal
import unittest

from src.itinerary.prompts import build_itinerary_prompt


class ItineraryPromptTests(unittest.TestCase):
    """Validate prompt data composition without contacting an AI provider."""

    def test_prompt_includes_all_trip_details_and_duration(self) -> None:
        prompt = build_itinerary_prompt(
            source="Mumbai",
            destination="Goa",
            start_date=date(2026, 9, 10),
            end_date=date(2026, 9, 12),
            budget=Decimal("25000.00"),
            travelers=2,
            preferences={"pace": "relaxed", "diet": "vegetarian"},
        )

        self.assertIn("Source: Mumbai", prompt)
        self.assertIn("Destination: Goa", prompt)
        self.assertIn("Duration: 3 days", prompt)
        self.assertIn("Total budget: 25000.00", prompt)
        self.assertIn('"diet": "vegetarian"', prompt)
        self.assertIn("food suggestions", prompt)


if __name__ == "__main__":
    unittest.main()
