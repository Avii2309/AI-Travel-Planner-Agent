"""Reusable prompt templates for itinerary generation."""

import json
from datetime import date
from decimal import Decimal
from typing import Any


SYSTEM_INSTRUCTIONS = """You are a practical, safety-conscious travel itinerary planner.
Create realistic plans using only the supplied trip details. Do not claim that bookings,
availability, prices, routes, or opening hours are guaranteed. Keep costs in the trip's
budget currency when it is known; otherwise state estimates as budget-relative values.
Return only JSON that conforms to the supplied schema."""

ITINERARY_REQUIREMENTS = """Generate exactly {duration} consecutive day entries numbered
from 1 to {duration}. Every day must include a balanced, geographically sensible sequence
of activities, sightseeing, food suggestions, local transport guidance, an estimated daily
cost, travel tips, and optional activities. Include overall packing tips and the best
visiting time. Costs must be non-negative numeric estimates and the total must cover all days."""


def build_itinerary_prompt(
    *,
    source: str,
    destination: str,
    start_date: date,
    end_date: date,
    budget: Decimal,
    travelers: int,
    preferences: dict[str, Any],
) -> str:
    """Build a deterministic, data-only prompt from an existing trip."""

    duration = (end_date - start_date).days + 1
    preferences_json = json.dumps(preferences, ensure_ascii=False, sort_keys=True)
    requirements = ITINERARY_REQUIREMENTS.format(duration=duration)
    return f"""Plan a trip using these confirmed details:
- Source: {source}
- Destination: {destination}
- Travel dates: {start_date.isoformat()} through {end_date.isoformat()}
- Duration: {duration} days
- Total budget: {budget}
- Travelers: {travelers}
- Preferences: {preferences_json}

{requirements}
"""
