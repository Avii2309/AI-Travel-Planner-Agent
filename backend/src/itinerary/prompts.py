"""Reusable prompt templates for itinerary generation."""

import json
from datetime import date
from decimal import Decimal
from typing import Any, Sequence

from src.locations.schemas import VerifiedPlace


SYSTEM_INSTRUCTIONS = """You are a practical, safety-conscious travel itinerary planner.
Create realistic plans using only the supplied trip details and verified Places. Do not invent
or name any real-world locations. Do not claim that bookings, availability, prices, routes,
or opening hours are guaranteed. Keep costs in the trip's budget currency when it is known;
otherwise state estimates as budget-relative values. Do not claim that a place is currently
open or provide opening hours; current hours are not verified.
Return only JSON that conforms to the supplied schema."""

ITINERARY_REQUIREMENTS = """Generate exactly {duration} consecutive day entries numbered
from 1 to {duration}. Every day must include a balanced, geographically sensible sequence
of activities using only the verified places below. Each activity must copy exactly one
Google Place ID from that list. Never add, alter, or infer a place ID, address, coordinate,
place name, opening time, or verification status. Do not repeat an attraction. The
sightseeing and optional_activities arrays may contain only verified place names or IDs.
Food entries may contain only verified restaurant names or IDs from the places below; omit
food entries if no verified restaurant is suitable. Never name an unverified venue. Include
local transport guidance without inventing route details, estimated daily costs, travel tips,
overall packing tips, and the best visiting time. Costs must be non-negative estimates."""


def build_itinerary_prompt(
    *,
    source: str,
    destination: str,
    start_date: date,
    end_date: date,
    budget: Decimal,
    travelers: int,
    preferences: dict[str, Any],
    verified_places: Sequence[VerifiedPlace],
) -> str:
    """Build a deterministic, data-only prompt from an existing trip."""

    duration = (end_date - start_date).days + 1
    preferences_json = json.dumps(preferences, ensure_ascii=False, sort_keys=True)
    places_json = json.dumps(
        [place.model_dump(mode="json") for place in verified_places],
        ensure_ascii=False,
        sort_keys=True,
    )
    requirements = ITINERARY_REQUIREMENTS.format(duration=duration)
    return f"""Plan a trip using these confirmed details:
- Source: {source}
- Destination: {destination}
- Travel dates: {start_date.isoformat()} through {end_date.isoformat()}
- Duration: {duration} days
- Total budget: {budget}
- Travelers: {travelers}
- Preferences: {preferences_json}

Google Places-verified attractions and restaurants (the only allowed real-world places):
{places_json}

{requirements}
"""
