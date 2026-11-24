"""Unit tests for the Gemini itinerary provider without network access."""

from types import SimpleNamespace
import unittest

from pydantic import SecretStr

from src.core.settings import TestingSettings
from src.itinerary.providers import (
    AIProviderExecutionError,
    AIProviderRateLimitError,
    AIProviderUnavailableError,
    GeminiProvider,
    get_ai_provider,
)


class StubModels:
    def __init__(self, response: object | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error

    async def generate_content(self, **_: object) -> object:
        if self.error is not None:
            raise self.error
        return self.response


class StubAio:
    def __init__(self, models: StubModels) -> None:
        self.models = models
        self.closed = False

    async def aclose(self) -> None:
        self.closed = True


class StubClient:
    def __init__(self, models: StubModels) -> None:
        self.aio = StubAio(models)


class TestGeminiProvider(GeminiProvider):
    def __init__(self, settings: TestingSettings, client: StubClient) -> None:
        super().__init__(settings)
        self.client = client

    def _create_client(self) -> StubClient:
        return self.client

    def _create_generation_config(self, response_schema: object) -> dict[str, object]:
        return {"schema": response_schema}


class GeminiProviderTests(unittest.IsolatedAsyncioTestCase):
    """Verify Gemini configuration and error translation at the provider boundary."""

    def _settings(self, key: str | None = "test-key") -> TestingSettings:
        return TestingSettings(
            debug=False,
            GEMINI_API_KEY=SecretStr(key) if key else None,
            GEMINI_MODEL="gemini-test",
        )

    def test_default_model_is_supported_flash_model(self) -> None:
        self.assertEqual(TestingSettings.model_fields["gemini_model"].default, "gemini-3.5-flash")

    async def test_generates_json_text_with_mocked_gemini_client(self) -> None:
        client = StubClient(StubModels(response=SimpleNamespace(text='{"days": []}')))
        provider = TestGeminiProvider(self._settings(), client)

        result = await provider.generate_itinerary("Plan a trip", {"type": "object"})

        self.assertEqual(result, '{"days": []}')
        self.assertTrue(client.aio.closed)

    async def test_rejects_missing_gemini_api_key(self) -> None:
        provider = TestGeminiProvider(self._settings(None), StubClient(StubModels()))

        with self.assertRaises(AIProviderUnavailableError):
            await provider.generate_itinerary("Plan a trip", {})

    async def test_translates_invalid_or_provider_failures(self) -> None:
        empty_provider = TestGeminiProvider(self._settings(), StubClient(StubModels(response=SimpleNamespace(text=""))))
        with self.assertRaises(AIProviderExecutionError):
            await empty_provider.generate_itinerary("Plan a trip", {})

        rate_limit_error = type("RateLimitError", (Exception,), {"code": 429})()
        rate_limited_provider = TestGeminiProvider(self._settings(), StubClient(StubModels(error=rate_limit_error)))
        with self.assertRaises(AIProviderRateLimitError):
            await rate_limited_provider.generate_itinerary("Plan a trip", {})

    async def test_provider_factory_uses_gemini_configuration(self) -> None:
        self.assertIsInstance(get_ai_provider(self._settings()), GeminiProvider)


if __name__ == "__main__":
    unittest.main()
