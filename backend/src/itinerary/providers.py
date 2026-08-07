"""AI provider boundary for itinerary generation."""

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


class OpenAIProvider(BaseAIProvider):
    """OpenAI Responses API implementation of the itinerary provider port."""

    def __init__(self, settings: AppSettings) -> None:
        self.api_key = settings.openai_api_key.get_secret_value() if settings.openai_api_key else None
        self.model = settings.openai_model
        self.timeout_seconds = settings.openai_timeout_seconds

    async def generate_itinerary(
        self,
        prompt: str,
        response_schema: Mapping[str, Any],
    ) -> str:
        """Request schema-constrained JSON from OpenAI without retaining trip data."""

        if not self.api_key:
            raise AIProviderUnavailableError("The AI provider is not configured.")

        try:
            from openai import (
                APIConnectionError,
                APIStatusError,
                APITimeoutError,
                AsyncOpenAI,
                RateLimitError,
            )
        except ImportError as error:
            raise AIProviderUnavailableError("The AI provider is not available.") from error

        client = AsyncOpenAI(api_key=self.api_key, timeout=self.timeout_seconds)
        started_at = time.perf_counter()
        try:
            response = await client.responses.create(
                model=self.model,
                instructions=SYSTEM_INSTRUCTIONS,
                input=prompt,
                store=False,
                text={
                    "format": {
                        "type": "json_schema",
                        "name": "travel_itinerary",
                        "strict": True,
                        "schema": dict(response_schema),
                    }
                },
            )
            output = response.output_text
            if not output:
                raise AIProviderExecutionError("The AI provider returned an empty response.")
            return output
        except APITimeoutError as error:
            get_error_logger().error("OpenAI itinerary request timed out")
            raise AIProviderTimeoutError("The AI provider timed out.") from error
        except RateLimitError as error:
            get_error_logger().error("OpenAI itinerary request was rate limited")
            raise AIProviderRateLimitError("The AI provider rate limit was reached.") from error
        except APIConnectionError as error:
            get_error_logger().error("OpenAI itinerary provider connection failed")
            raise AIProviderUnavailableError("The AI provider is temporarily unavailable.") from error
        except APIStatusError as error:
            get_error_logger().error("OpenAI itinerary provider returned status %s", error.status_code)
            if error.status_code >= 500:
                raise AIProviderUnavailableError("The AI provider is temporarily unavailable.") from error
            raise AIProviderExecutionError("The AI provider could not generate an itinerary.") from error
        except AIProviderError:
            raise
        except Exception as error:
            get_error_logger().exception("OpenAI itinerary provider failed", exc_info=error)
            raise AIProviderExecutionError("The AI provider could not generate an itinerary.") from error
        finally:
            elapsed_ms = (time.perf_counter() - started_at) * 1000
            get_application_logger().info("OpenAI itinerary provider finished in %.2f ms", elapsed_ms)
            await client.close()


def get_ai_provider(settings: AppSettings) -> BaseAIProvider:
    """Construct the configured AI provider behind the stable provider interface."""

    return OpenAIProvider(settings)
