"""Tests for Geoapify forward geocoding and safe result selection."""

from types import SimpleNamespace
import unittest
from unittest.mock import patch

import httpx
from pydantic import SecretStr

from src.core.settings import TestingSettings
from src.locations.geoapify import (
    GEOAPIFY_FORWARD_GEOCODING_URL,
    GeoapifyConfigurationError,
    GeoapifyProvider,
    GeoapifyUnavailableError,
    resolve_geocoded_location,
)


class StubHTTPClient:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.request: tuple[object, dict[str, object]] | None = None

    async def __aenter__(self) -> "StubHTTPClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def get(self, url: object, **kwargs: object) -> object:
        if self.error is not None:
            raise self.error
        self.request = (url, kwargs)
        return self.response


def geo_result(
    name: str,
    formatted: str,
    latitude: float,
    longitude: float,
    *,
    place_id: str | None = None,
    result_type: str = "city",
) -> dict[str, object]:
    return {
        "place_id": place_id,
        "name": name,
        "formatted": formatted,
        "result_type": result_type,
        "lat": latitude,
        "lon": longitude,
    }


class GeoapifyTests(unittest.IsolatedAsyncioTestCase):
    def _provider(self, key: str | None = "test-key") -> GeoapifyProvider:
        return GeoapifyProvider(
            TestingSettings(
                GEOAPIFY_API_KEY=SecretStr(key) if key is not None else None,
                APP_TIMEZONE="Asia/Kolkata",
            )
        )

    async def test_forward_geocode_uses_server_key_and_expected_endpoint(self) -> None:
        response = SimpleNamespace(is_error=False, json=lambda: {"results": []})
        client = StubHTTPClient(response=response)
        provider = self._provider()
        with patch("src.locations.geoapify.httpx.AsyncClient", return_value=client):
            self.assertEqual(await provider.geocode("Jaipur, Rajasthan"), [])

        assert client.request is not None
        url, request = client.request
        self.assertEqual(url, GEOAPIFY_FORWARD_GEOCODING_URL)
        params = request["params"]
        self.assertEqual(params["text"], "Jaipur, Rajasthan")
        self.assertEqual(params["apiKey"], "test-key")
        self.assertEqual(params["format"], "json")

    async def test_missing_key_and_transport_failure_are_service_errors(self) -> None:
        with self.assertRaises(GeoapifyConfigurationError):
            await self._provider(None).geocode("Jaipur")

        with patch(
            "src.locations.geoapify.httpx.AsyncClient",
            return_value=StubHTTPClient(error=httpx.TimeoutException("timeout")),
        ):
            with self.assertRaises(GeoapifyUnavailableError):
                await self._provider().geocode("Jaipur")

    async def test_selects_one_matching_location_and_rejects_unrelated_or_ambiguous_results(self) -> None:
        jaipur = geo_result(
            "Jaipur",
            "Jaipur, Rajasthan, India",
            26.9124,
            75.7873,
            place_id="jaipur",
        )
        unrelated = geo_result("Delhi", "Delhi, India", 28.6139, 77.209, place_id="delhi")
        location, ambiguous = resolve_geocoded_location("Jaipur, Rajasthan", [unrelated, jaipur])
        self.assertFalse(ambiguous)
        self.assertIsNotNone(location)
        assert location is not None
        self.assertEqual(location.name, "Jaipur")
        self.assertEqual(location.place_id, "jaipur")

        invalid, ambiguous = resolve_geocoded_location("InvalidXYZ123", [jaipur])
        self.assertIsNone(invalid)
        self.assertFalse(ambiguous)

        second_jaipur = geo_result(
            "Jaipur",
            "Jaipur, Rajasthan, India",
            27.1,
            76.0,
            place_id="another-jaipur",
        )
        invalid, ambiguous = resolve_geocoded_location("Jaipur, Rajasthan", [jaipur, second_jaipur])
        self.assertIsNone(invalid)
        self.assertTrue(ambiguous)

    def test_rejects_non_geographical_results_and_invalid_coordinates(self) -> None:
        results = [
            geo_result("Jaipur", "Jaipur, Rajasthan, India", 26.9, 75.8, result_type="unknown"),
            geo_result("Jaipur", "Jaipur, Rajasthan, India", 91, 75.8),
        ]
        location, ambiguous = resolve_geocoded_location("Jaipur, Rajasthan", results)
        self.assertIsNone(location)
        self.assertFalse(ambiguous)


if __name__ == "__main__":
    unittest.main()
