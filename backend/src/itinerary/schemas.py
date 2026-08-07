"""Validated contracts for generated travel itineraries."""

import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class ItineraryActivity(BaseModel):
    """One scheduled activity within an itinerary day."""

    model_config = ConfigDict(extra="forbid")

    time: str = Field(description="Suggested local time or time range")
    title: str = Field(description="Short activity name")
    description: str = Field(description="Practical activity details")
    location: str = Field(description="Place or neighborhood")
    estimated_cost: float = Field(ge=0, description="Estimated cost in the trip budget currency")


class ItineraryDay(BaseModel):
    """A complete plan for one day of a trip."""

    model_config = ConfigDict(extra="forbid")

    day: int = Field(ge=1)
    title: str
    activities: list[ItineraryActivity]
    sightseeing: list[str]
    food: list[str]
    transport: str
    estimated_cost: float = Field(ge=0)
    travel_tips: list[str]
    optional_activities: list[str]


class GeneratedItinerary(BaseModel):
    """Structured content returned by an AI provider before API metadata is added."""

    model_config = ConfigDict(extra="forbid")

    days: list[ItineraryDay] = Field(min_length=1)
    summary: str
    estimated_total_cost: float = Field(ge=0)
    packing_tips: list[str]
    best_visiting_time: str


class ItineraryResponse(GeneratedItinerary):
    """The generated itinerary returned to the authenticated trip owner."""

    trip_id: UUID
    generated_at: datetime


class InvalidItineraryResponseError(Exception):
    """Raised when an AI provider returns non-conforming itinerary content."""


def itinerary_response_schema() -> dict[str, Any]:
    """Return the JSON Schema used by providers that support structured output."""

    return GeneratedItinerary.model_json_schema()


def parse_itinerary_response(
    raw_response: str,
    *,
    trip_id: UUID,
    generated_at: datetime,
    expected_days: int,
) -> ItineraryResponse:
    """Validate provider JSON and add server-owned response metadata."""

    try:
        content = GeneratedItinerary.model_validate(json.loads(raw_response))
    except (json.JSONDecodeError, ValidationError, TypeError) as error:
        raise InvalidItineraryResponseError("AI returned an invalid itinerary format.") from error

    actual_days = [day.day for day in content.days]
    if actual_days != list(range(1, expected_days + 1)):
        raise InvalidItineraryResponseError(
            "AI returned itinerary days that do not match the trip duration."
        )

    return ItineraryResponse(
        trip_id=trip_id,
        generated_at=generated_at,
        **content.model_dump(),
    )
