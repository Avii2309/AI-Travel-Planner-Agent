"""Tests for date validation in the configured application timezone."""

from datetime import date
import unittest

from src.trips.service import TripDateValidationError, validate_trip_dates


class TripDateValidationTests(unittest.TestCase):
    def test_rejects_past_start_date(self) -> None:
        with self.assertRaisesRegex(
            TripDateValidationError,
            "Trip start date cannot be in the past. Please select today or a future date.",
        ) as raised:
            validate_trip_dates(
                date(2026, 11, 18),
                date(2026, 11, 19),
                timezone_name="Asia/Kolkata",
                today=date(2026, 11, 19),
            )
        self.assertEqual(raised.exception.code, "PAST_START_DATE")
        self.assertEqual(raised.exception.field, "start_date")

    def test_allows_today_same_day_and_future_dates(self) -> None:
        for start_date, end_date in (
            (date(2026, 11, 19), date(2026, 11, 19)),
            (date(2026, 11, 20), date(2026, 11, 20)),
            (date(2026, 12, 25), date(2026, 12, 27)),
        ):
            with self.subTest(start_date=start_date):
                validate_trip_dates(
                    start_date,
                    end_date,
                    timezone_name="Asia/Kolkata",
                    today=date(2026, 11, 19),
                )

    def test_rejects_end_before_start(self) -> None:
        with self.assertRaisesRegex(TripDateValidationError, "End date") as raised:
            validate_trip_dates(
                date(2026, 11, 20),
                date(2026, 11, 19),
                timezone_name="Asia/Kolkata",
                today=date(2026, 11, 19),
            )
        self.assertEqual(raised.exception.code, "INVALID_DATE_RANGE")
        self.assertEqual(raised.exception.field, "end_date")


if __name__ == "__main__":
    unittest.main()
