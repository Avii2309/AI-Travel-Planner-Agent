"""Contracts for Google Places-verified destinations and attractions."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class VerifiedPlace(BaseModel):
    """Place identity and coordinates returned by Google Places."""

    model_config = ConfigDict(extra="forbid")

    place_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    formatted_address: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    types: list[str] = Field(default_factory=list)


class VerifiedGeocodedLocation(BaseModel):
    """Canonical location details returned by Geoapify."""

    model_config = ConfigDict(extra="forbid")

    place_id: str | None = None
    name: str = Field(min_length=1)
    formatted_address: str = Field(min_length=1)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class LocationVerificationResponse(VerifiedPlace):
    """Successful response from the destination verification endpoint."""

    success: Literal[True] = True
