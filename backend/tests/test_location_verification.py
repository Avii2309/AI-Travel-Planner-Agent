"""Tests for Google Places response classification and destination resolution."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
from pydantic import SecretStr

from src.core.settings import TestingSettings
from src.locations.providers import (
    GooglePlacesAuthenticationError,
    GooglePlacesBillingError,
    GooglePlacesProvider,
    GooglePlacesQuotaExceededError,
    GooglePlacesUnavailableError,
)
from src.locations.router import LocationVerificationRequest, verify_location as verify_location_route
from src.locations.service import InvalidLocationError, verify_destination


class StubSearchProvider:
    def __init__(self, places: list[dict[str, object]]) -> None:
        self.places = places

    async def search_text(self, *_: object, **__: object) -> list[dict[str, object]]:
        return self.places


class StubHTTPClient:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.request: tuple[object, dict[str, object]] | None = None

    async def __aenter__(self) -> "StubHTTPClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def post(self, url: object, **kwargs: object) -> object:
        if self.error is not None:
            raise self.error
        self.request = (url, kwargs)
        return self.response


class EmptySearchProvider:
    async def search_text(self, *_: object, **__: object) -> list[dict[str, object]]:
        return []


class FailedSearchProvider:
    async def search_text(self, *_: object, **__: object) -> list[dict[str, object]]:
        raise GooglePlacesUnavailableError("Provider unavailable")


class LocationVerificationTests(unittest.IsolatedAsyncioTestCase):
    def _provider(self) -> GooglePlacesProvider:
        settings = TestingSettings(
            GOOGLE_PLACES_API_KEY=SecretStr("test-key"),
            APP_TIMEZONE="Asia/Kolkata",
        )
        return GooglePlacesProvider(settings)

    async def test_missing_google_key_is_a_configuration_error(self) -> None:
        settings = TestingSettings(
            GOOGLE_PLACES_API_KEY=None,
            GOOGLE_MAPS_API_KEY=None,
            APP_TIMEZONE="Asia/Kolkata",
        )
        with self.assertRaisesRegex(
            GooglePlacesUnavailableError,
            "Set GOOGLE_PLACES_API_KEY or GOOGLE_MAPS_API_KEY",
        ):
            await GooglePlacesProvider(settings).search_text("Jaipur, Rajasthan, India")

    async def test_empty_google_result_is_invalid_location(self) -> None:
        with self.assertRaises(InvalidLocationError):
            await verify_destination("XYZ Unknown City 12345", EmptySearchProvider())  # type: ignore[arg-type]

    async def test_unrelated_google_result_is_not_accepted_as_destination(self) -> None:
        unrelated = {
            "id": "unrelated-place",
            "displayName": {"text": "Known Place"},
            "formattedAddress": "Known Place, Region",
            "location": {"latitude": 10, "longitude": 20},
            "types": ["locality"],
        }
        with self.assertRaises(InvalidLocationError):
            await verify_destination(
                "XYZ Unknown City 12345",
                StubSearchProvider([unrelated]),  # type: ignore[arg-type]
            )

    async def test_invalid_location_route_returns_requested_error_shape(self) -> None:
        response = await verify_location_route(
            LocationVerificationRequest(destination="XYZ Unknown City 12345"),
            object(),
            EmptySearchProvider(),  # type: ignore[arg-type]
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(
            response.body.decode("utf-8"),
            (
                '{"success":false,"error":"INVALID_LOCATION","message":'
                '"The entered destination could not be verified. Please enter a valid location."}'
            ),
        )

    async def test_places_service_failure_returns_service_error_not_invalid_location(self) -> None:
        response = await verify_location_route(
            LocationVerificationRequest(destination="Known City"),
            object(),
            FailedSearchProvider(),  # type: ignore[arg-type]
        )
        self.assertEqual(response.status_code, 503)
        self.assertIn(b'"error":"GOOGLE_PLACES_UNAVAILABLE"', response.body)

    def test_maps_api_key_is_used_if_places_key_is_blank(self) -> None:
        settings = TestingSettings(
            GOOGLE_PLACES_API_KEY=SecretStr(" "),
            GOOGLE_MAPS_API_KEY=SecretStr("maps-platform-key"),
            APP_TIMEZONE="Asia/Kolkata",
        )
        self.assertEqual(
            settings.effective_google_places_api_key.get_secret_value(),
            "maps-platform-key",
        )

    async def test_places_service_failure_is_not_invalid_location(self) -> None:
        provider = self._provider()

        with patch(
            "src.locations.providers.httpx.AsyncClient",
            return_value=StubHTTPClient(error=httpx.TimeoutException("timeout")),
        ):
            with self.assertRaises(GooglePlacesUnavailableError):
                await provider.search_text("A destination")

    async def test_request_uses_places_api_new_with_backend_key(self) -> None:
        provider = self._provider()
        response = SimpleNamespace(status_code=200, is_error=False, json=lambda: {"places": []})
        client = StubHTTPClient(response=response)
        with patch("src.locations.providers.httpx.AsyncClient", return_value=client):
            await provider.search_text("Example destination")

        self.assertIsNotNone(client.request)
        url, request = client.request
        self.assertEqual(url, "https://places.googleapis.com/v1/places:searchText")
        headers = request["headers"]
        body = request["json"]
        self.assertEqual(headers["X-Goog-Api-Key"], "test-key")
        self.assertIn("places.id", headers["X-Goog-FieldMask"])
        self.assertEqual(body["textQuery"], "Example destination")

    async def test_places_quota_is_classified_separately(self) -> None:
        provider = self._provider()
        response = SimpleNamespace(
            status_code=429,
            is_error=True,
            json=lambda: {"error": {"status": "RESOURCE_EXHAUSTED"}},
        )
        with patch(
            "src.locations.providers.httpx.AsyncClient",
            return_value=StubHTTPClient(response=response),
        ):
            with self.assertRaises(GooglePlacesQuotaExceededError):
                await provider.search_text("A destination")

    async def test_api_key_and_billing_errors_are_not_reported_as_invalid_locations(self) -> None:
        provider = self._provider()
        cases = (
            (
                403,
                {"error": {"status": "PERMISSION_DENIED", "message": "API key invalid"}},
                GooglePlacesAuthenticationError,
            ),
            (
                403,
                {"error": {"status": "PERMISSION_DENIED", "message": "Billing is disabled"}},
                GooglePlacesBillingError,
            ),
        )
        for status_code, body, expected_error in cases:
            response = SimpleNamespace(
                status_code=status_code,
                is_error=True,
                json=lambda payload=body: payload,
            )
            with self.subTest(expected_error=expected_error.__name__):
                with patch(
                    "src.locations.providers.httpx.AsyncClient",
                    return_value=StubHTTPClient(response=response),
                ):
                    with self.assertRaises(expected_error):
                        await provider.search_text("A destination")
if __name__ == "__main__":
    unittest.main()
