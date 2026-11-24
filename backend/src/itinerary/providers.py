"""AI provider boundary for itinerary generation."""

import inspect
import time
from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from src.core.logger import get_application_logger, get_error_logger
from src.core.settings import AppSettings
from src.itinerary.prompts import SYSTEM_INSTRUCTIONS


class AIProviderError(Exception):
    """Base error raised for provider failures that are safe to expose at the API boundary."""


class AIProviderUnavailableError(AIProviderError):
    """Raised when a configured provider cannot be used."""


class AIProviderTimeoutError(AIProviderError):
    """Raised when a provider does not respond within its configured timeout."""


class AIProviderRateLimitError(AIProviderError):
    """Raised when a provider rejects a request due to rate limiting."""


class AIProviderExecutionError(AIProviderError):
    """Raised for an unexpected provider execution failure."""


class BaseAIProvider(ABC):
    """Stable interface implemented by all itinerary AI providers."""

    @abstractmethod
    async def generate_itinerary(
        self,
        prompt: str,
        response_schema: Mapping[str, Any],
    ) -> str:
        """Return the provider's JSON itinerary output."""


class GeminiProvider(BaseAIProvider):
    """Google Gemini implementation of the itinerary provider port."""

    def __init__(self, settings: AppSettings) -> None:
        self.api_key = settings.gemini_api_key.get_secret_value() if settings.gemini_api_key else None
        self.model = settings.gemini_model
        self.timeout_seconds = settings.gemini_timeout_seconds

    def _create_client(self) -> Any:
        """Import the SDK lazily so missing optional dependencies fail safely."""

        try:
            from google import genai
        except ImportError as error:
            raise AIProviderUnavailableError("The AI provider is not available.") from error
        return genai.Client(api_key=self.api_key)

    def _create_generation_config(self, response_schema: Mapping[str, Any]) -> Any:
        """Build Gemini's structured-output configuration from the shared schema."""

        try:
            from google.genai import types
        except ImportError as error:
            raise AIProviderUnavailableError("The AI provider is not available.") from error
        return types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTIONS,
            response_mime_type="application/json",
            response_json_schema=dict(response_schema),
            http_options=types.HttpOptions(timeout=int(self.timeout_seconds * 1000)),
        )

    async def generate_itinerary(
        self,
        prompt: str,
        response_schema: Mapping[str, Any],
    ) -> str:
        """Request schema-constrained JSON from Gemini without retaining trip data."""

        if not self.api_key:
            raise AIProviderUnavailableError("The AI provider is not configured.")

        client = self._create_client()
        started_at = time.perf_counter()
        try:
            response = await client.aio.models.generate_content(
                model=self.model,
                contents=prompt,
                config=self._create_generation_config(response_schema),
            )
            output = response.text
            if not output:
                raise AIProviderExecutionError("The AI provider returned an empty response.")
            return output
        except AIProviderError:
            raise
        except Exception as error:
            status_code = getattr(error, "code", None) or getattr(error, "status_code", None)
            error_name = type(error).__name__.lower()
            if status_code == 429:
                get_error_logger().error("Gemini itinerary request was rate limited")
                raise AIProviderRateLimitError("The AI provider rate limit was reached.") from error
            if status_code in {408, 504} or "timeout" in error_name:
                get_error_logger().error("Gemini itinerary request timed out")
                raise AIProviderTimeoutError("The AI provider timed out.") from error
            if isinstance(status_code, int) and status_code >= 500:
                get_error_logger().error("Gemini itinerary provider returned status %s", status_code)
                raise AIProviderUnavailableError("The AI provider is temporarily unavailable.") from error
            if "connection" in error_name or "network" in error_name:
                get_error_logger().error("Gemini itinerary provider connection failed")
                raise AIProviderUnavailableError("The AI provider is temporarily unavailable.") from error
            get_error_logger().exception("Gemini itinerary provider failed", exc_info=error)
            raise AIProviderExecutionError("The AI provider could not generate an itinerary.") from error
        finally:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            get_application_logger().info("Gemini itinerary provider finished in %.2f ms", elapsed_ms)
            close = getattr(client.aio, "aclose", None)
            if close is not None:
                close_result = close()
                if inspect.isawaitable(close_result):
                    await close_result


def get_ai_provider(settings: AppSettings) -> BaseAIProvider:
    """Construct the configured AI provider behind the stable provider interface."""

    return GeminiProvider(settings)
