"""Tests for trip validation before persistence."""

from datetime import datetime, timedelta
from decimal import Decimal
import json
from types import SimpleNamespace
import unittest
from unittest.mock import patch
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import Request
from fastapi.exceptions import RequestValidationError

from src.locations.geoapify import GeoapifyConfigurationError, GeoapifyUnavailableError
from src.presentation.api.exceptions.handlers import handle_validation_exception
from src.trips.schemas import TripCreate
from src.trips.router import create as create_trip_route
from src.trips.service import (
    TripDateValidationError,
    TripLocationServiceError,
    TripLocationValidationError,
    create_trip,
)


def result(name: str, address: str, latitude: float, longitude: float, place_id: str) -> dict[str, object]:
    return {
        "name": name,
        "formatted": address,
        "lat": latitude,
        "lon": longitude,
        "place_id": place_id,
        "result_type": "city",
    }


class StubGeoapifyProvider:
    def __init__(self, results: dict[str, list[dict[str, object]] | Exception]) -> None:
        self.results = results
        self.queries: list[str] = []

    async def geocode(self, query: str) -> list[dict[str, object]]:
        self.queries.append(query)
        response = self.results[query]
        if isinstance(response, Exception):
            raise response
        return response


class StubTripRepository:
    def __init__(self) -> None:
        self.saved: dict[str, object] | None = None

    async def create(self, user_id: object, values: dict[str, object]) -> object:
        self.saved = values
        return SimpleNamespace(user_id=user_id, **values)


class TripCreationValidationTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        self.future_date = today + timedelta(days=30)
        self.request = TripCreate(
            source="Jaipur, Rajasthan",
            destination="Delhi, India",
            start_date=self.future_date,
            end_date=self.future_date,
            budget=Decimal("1000"),
            travelers=1,
        )
        self.user = SimpleNamespace(id=uuid4())
        self.repository = StubTripRepository()
        self.repository_patch = patch("src.trips.service.TripRepository", return_value=self.repository)
        self.repository_patch.start()
        self.addCleanup(self.repository_patch.stop)

    def _provider(self) -> StubGeoapifyProvider:
        return StubGeoapifyProvider(
            {
                "Jaipur, Rajasthan": [
                    result("Jaipur", "Jaipur, Rajasthan, India", 26.9124, 75.7873, "jaipur-id")
                ],
                "Delhi, India": [result("Delhi", "Delhi, India", 28.6139, 77.209, "delhi-id")],
            }
        )

    async def test_valid_locations_are_independently_verified_before_saving(self) -> None:
        provider = self._provider()
        trip = await create_trip(
            object(),  # type: ignore[arg-type]
            self.user,  # type: ignore[arg-type]
            self.request,
            geoapify_provider=provider,  # type: ignore[arg-type]
            timezone_name="Asia/Kolkata",
        )

        self.assertEqual(provider.queries, ["Jaipur, Rajasthan", "Delhi, India"])
        self.assertEqual(self.repository.saved["source_place_id"], "jaipur-id")  # type: ignore[index]
        self.assertEqual(self.repository.saved["source_name"], "Jaipur")  # type: ignore[index]
        self.assertEqual(self.repository.saved["destination_place_id"], "delhi-id")  # type: ignore[index]
        self.assertEqual(trip.destination_name, "Delhi")

    async def test_invalid_start_or_destination_never_persists(self) -> None:
        provider = self._provider()
        provider.results["Jaipur, Rajasthan"] = []
        with self.assertRaises(TripLocationValidationError) as raised:
            await create_trip(
                object(),  # type: ignore[arg-type]
                self.user,  # type: ignore[arg-type]
                self.request,
                geoapify_provider=provider,  # type: ignore[arg-type]
                timezone_name="Asia/Kolkata",
            )
        self.assertEqual(raised.exception.code, "INVALID_START_LOCATION")
        self.assertEqual(raised.exception.field, "start_location")
        self.assertIsNone(self.repository.saved)
        self.assertEqual(provider.queries, ["Jaipur, Rajasthan"])

        provider = self._provider()
        provider.results["Delhi, India"] = []
        with self.assertRaises(TripLocationValidationError) as raised:
            await create_trip(
                object(),  # type: ignore[arg-type]
                self.user,  # type: ignore[arg-type]
                self.request,
                geoapify_provider=provider,  # type: ignore[arg-type]
                timezone_name="Asia/Kolkata",
            )
        self.assertEqual(raised.exception.code, "INVALID_DESTINATION")
        self.assertEqual(raised.exception.field, "destination")
        self.assertIsNone(self.repository.saved)

    async def test_dates_are_checked_before_geocoding_and_persistence(self) -> None:
        provider = self._provider()
        past_request = self.request.model_copy(
            update={"start_date": self.future_date - timedelta(days=60)}
        )
        with self.assertRaises(TripDateValidationError) as raised:
            await create_trip(
                object(),  # type: ignore[arg-type]
                self.user,  # type: ignore[arg-type]
                past_request,
                geoapify_provider=provider,  # type: ignore[arg-type]
                timezone_name="Asia/Kolkata",
            )
        self.assertEqual(raised.exception.code, "PAST_START_DATE")
        self.assertEqual(provider.queries, [])
        self.assertIsNone(self.repository.saved)

        invalid_range = self.request.model_copy(
            update={"end_date": self.future_date - timedelta(days=1)}
        )
        with self.assertRaises(TripDateValidationError) as raised:
            await create_trip(
                object(),  # type: ignore[arg-type]
                self.user,  # type: ignore[arg-type]
                invalid_range,
                geoapify_provider=provider,  # type: ignore[arg-type]
                timezone_name="Asia/Kolkata",
            )
        self.assertEqual(raised.exception.code, "INVALID_DATE_RANGE")
        self.assertEqual(provider.queries, [])
        self.assertIsNone(self.repository.saved)

    async def test_unavailable_or_unconfigured_geoapify_never_persists(self) -> None:
        for provider_error, expected_code in (
            (GeoapifyUnavailableError(), "LOCATION_VERIFICATION_UNAVAILABLE"),
            (GeoapifyConfigurationError(), "LOCATION_VERIFICATION_NOT_CONFIGURED"),
        ):
            provider = StubGeoapifyProvider({"Jaipur, Rajasthan": provider_error})
            with self.subTest(expected_code=expected_code):
                with self.assertRaises(TripLocationServiceError) as raised:
                    await create_trip(
                        object(),  # type: ignore[arg-type]
                        self.user,  # type: ignore[arg-type]
                        self.request,
                        geoapify_provider=provider,  # type: ignore[arg-type]
                        timezone_name="Asia/Kolkata",
                    )
                self.assertEqual(raised.exception.code, expected_code)
                self.assertEqual(raised.exception.field, "start_location")
                self.assertIsNone(self.repository.saved)

    async def test_trip_endpoint_returns_field_specific_422_and_503_errors(self) -> None:
        settings = SimpleNamespace(application_timezone="Asia/Kolkata")
        invalid_provider = StubGeoapifyProvider({"Jaipur, Rajasthan": []})
        invalid_response = await create_trip_route(
            self.request,
            object(),  # type: ignore[arg-type]
            self.user,  # type: ignore[arg-type]
            invalid_provider,  # type: ignore[arg-type]
            settings,  # type: ignore[arg-type]
        )
        self.assertEqual(invalid_response.status_code, 422)  # type: ignore[union-attr]
        invalid_body = json.loads(invalid_response.body)  # type: ignore[union-attr]
        self.assertEqual(invalid_body["error_code"], "INVALID_START_LOCATION")
        self.assertEqual(invalid_body["field"], "start_location")

        unavailable_provider = StubGeoapifyProvider(
            {"Jaipur, Rajasthan": GeoapifyUnavailableError()}
        )
        unavailable_response = await create_trip_route(
            self.request,
            object(),  # type: ignore[arg-type]
            self.user,  # type: ignore[arg-type]
            unavailable_provider,  # type: ignore[arg-type]
            settings,  # type: ignore[arg-type]
        )
        self.assertEqual(unavailable_response.status_code, 503)  # type: ignore[union-attr]
        unavailable_body = json.loads(unavailable_response.body)  # type: ignore[union-attr]
        self.assertEqual(unavailable_body["error_code"], "LOCATION_VERIFICATION_UNAVAILABLE")
        self.assertEqual(unavailable_body["field"], "start_location")
        self.assertIsNone(self.repository.saved)

    async def test_ambiguous_location_is_rejected_without_persistence(self) -> None:
        provider = self._provider()
        provider.results["Jaipur, Rajasthan"] = [
            result("Jaipur", "Jaipur, Rajasthan, India", 26.9124, 75.7873, "jaipur-id"),
            result("Jaipur", "Jaipur, Rajasthan, India", 27.1, 76.0, "another-jaipur-id"),
        ]
        with self.assertRaises(TripLocationValidationError) as raised:
            await create_trip(
                object(),  # type: ignore[arg-type]
                self.user,  # type: ignore[arg-type]
                self.request,
                geoapify_provider=provider,  # type: ignore[arg-type]
                timezone_name="Asia/Kolkata",
            )
        self.assertEqual(raised.exception.code, "AMBIGUOUS_START")
        self.assertIn("more specific", str(raised.exception))
        self.assertIsNone(self.repository.saved)

    async def test_today_same_day_dates_are_allowed(self) -> None:
        today = datetime.now(ZoneInfo("Asia/Kolkata")).date()
        request = self.request.model_copy(update={"start_date": today, "end_date": today})
        trip = await create_trip(
            object(),  # type: ignore[arg-type]
            self.user,  # type: ignore[arg-type]
            request,
            geoapify_provider=self._provider(),  # type: ignore[arg-type]
            timezone_name="Asia/Kolkata",
        )
        self.assertEqual(trip.start_date, today)
        self.assertIsNotNone(self.repository.saved)

    async def test_missing_and_malformed_dates_return_structured_errors(self) -> None:
        request = Request(
            {
                "type": "http",
                "method": "POST",
                "path": "/api/v1/trips",
                "headers": [],
                "query_string": b"",
            }
        )
        for field in ("start_date", "end_date"):
            error = RequestValidationError(
                [
                    {
                        "type": "date_from_datetime_parsing",
                        "loc": ("body", field),
                        "msg": "Input should be a valid date",
                        "input": "not-a-date",
                    }
                ]
            )
            response = await handle_validation_exception(request, error)
            self.assertEqual(response.status_code, 422)
            self.assertIn(b'"error_code":"INVALID_DATE"', response.body)
            self.assertIn(f'"field":"{field}"'.encode(), response.body)


if __name__ == "__main__":
    unittest.main()
