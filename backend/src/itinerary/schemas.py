"""Validated contracts for generated travel itineraries."""

import json
from datetime import date, datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from src.locations.schemas import VerifiedPlace


class ItineraryActivity(BaseModel):
    """One scheduled activity within an itinerary day."""

    model_config = ConfigDict(extra="forbid")

    time: str = Field(description="Suggested local time or time range")
    title: str = Field(description="Short activity name")
    description: str = Field(description="Practical activity details")
    location: str = Field(description="Place or neighborhood")
    estimated_cost: float = Field(ge=0, description="Estimated cost in the trip budget currency")
    place_id: str | None = Field(
        default=None,
        description="Google Place ID copied from the verified places supplied to the model",
    )


class ItineraryDay(BaseModel):
    """A complete plan for one day of a trip."""

    model_config = ConfigDict(extra="forbid")

    day: int = Field(ge=1)
    title: str
    activities: list[ItineraryActivity]
    sightseeing: list[str] = Field(
        description="Only exact verified tourist attraction names or their Google Place IDs",
    )
    food: list[str] = Field(
        description="Only exact verified restaurant names or their Google Place IDs; may be empty",
    )
    transport: str
    estimated_cost: float = Field(ge=0)
    travel_tips: list[str]
    optional_activities: list[str] = Field(
        description="Only exact verified tourist attraction names or their Google Place IDs",
    )


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
    verified_places: list[VerifiedPlace] = Field(default_factory=list)


class ItineraryListItem(BaseModel):
    """Lightweight saved-itinerary metadata for the authenticated user's list."""

    trip_id: UUID
    destination: str
    start_date: date
    end_date: date
    generated_at: datetime


class InvalidItineraryResponseError(Exception):
    """Raised when an AI provider returns non-conforming itinerary content."""


def itinerary_response_schema() -> dict[str, Any]:
    """Return the JSON Schema used by providers that support structured output."""

    schema = GeneratedItinerary.model_json_schema()
    activity_schema = schema["$defs"]["ItineraryActivity"]
    activity_schema["properties"]["place_id"] = {
        "type": "string",
        "description": "Required Google Place ID copied exactly from the verified places",
    }
    activity_schema["required"].append("place_id")
    return schema


def parse_itinerary_response(
    raw_response: str,
    *,
    trip_id: UUID,
    generated_at: datetime,
    expected_days: int,
    verified_places: list[VerifiedPlace] | None = None,
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

    if verified_places is not None:
        attractions_by_id = {
            place.place_id: place for place in verified_places if "tourist_attraction" in place.types
        }
        attractions_by_name = {
            place.name.casefold(): place for place in verified_places if "tourist_attraction" in place.types
        }
        restaurants_by_id = {
            place.place_id: place for place in verified_places if "restaurant" in place.types
        }
        restaurants_by_name = {
            place.name.casefold(): place for place in verified_places if "restaurant" in place.types
        }
        selected_ids: set[str] = set()

        def canonical_name(
            value: str,
            by_id: dict[str, VerifiedPlace],
            by_name: dict[str, VerifiedPlace],
        ) -> str:
            place = by_id.get(value) or by_name.get(value.casefold())
            if place is None:
                raise InvalidItineraryResponseError(
                    "AI returned a place that was not verified by Google Places."
                )
            return place.name

        for day in content.days:
            if not day.activities:
                raise InvalidItineraryResponseError(
                    "AI returned a day without a verified attraction."
                )
            for activity in day.activities:
                place = attractions_by_id.get(activity.place_id or "")
                if place is None or place.place_id in selected_ids:
                    raise InvalidItineraryResponseError(
                        "AI returned an unverified or repeated attraction."
                    )
                selected_ids.add(place.place_id)
                activity.title = place.name
                activity.location = place.formatted_address
            day.sightseeing = [
                canonical_name(item, attractions_by_id, attractions_by_name)
                for item in day.sightseeing
            ]
            day.optional_activities = [
                canonical_name(item, attractions_by_id, attractions_by_name)
                for item in day.optional_activities
            ]
            day.food = [
                canonical_name(item, restaurants_by_id, restaurants_by_name)
                for item in day.food
            ]

    return ItineraryResponse(
        trip_id=trip_id,
        generated_at=generated_at,
        verified_places=verified_places or [],
        **content.model_dump(),
    )
