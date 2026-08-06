"""Request and response contracts for trip management."""

from datetime import date, datetime
from decimal import Decimal
from typing import Annotated, Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Location = Annotated[str, Field(min_length=1, max_length=255)]
Budget = Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
Travelers = Annotated[int, Field(ge=1, le=100)]


class TripCreate(BaseModel):
    """Validated input for creating a trip."""

    source: Location
    destination: Location
    start_date: date
    end_date: date
    budget: Budget
    travelers: Travelers
    preferences: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source", "destination")
    @classmethod
    def normalize_location(cls, value: str) -> str:
        """Reject whitespace-only locations and normalize visible spacing."""

        normalized_value = " ".join(value.split())
        if not normalized_value:
            raise ValueError("location must contain non-whitespace characters")
        return normalized_value

    @model_validator(mode="after")
    def validate_date_range(self) -> "TripCreate":
        """Require an end date on or after the start date."""

        if self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class TripUpdate(BaseModel):
    """Partial update input for a user-owned trip."""

    source: Location | None = None
    destination: Location | None = None
    start_date: date | None = None
    end_date: date | None = None
    budget: Budget | None = None
    travelers: Travelers | None = None
    preferences: dict[str, Any] = Field(default_factory=dict)

    @field_validator("source", "destination")
    @classmethod
    def normalize_location(cls, value: str | None) -> str | None:
        """Normalize supplied locations."""

        if value is None:
            return value
        normalized_value = " ".join(value.split())
        if not normalized_value:
            raise ValueError("location must contain non-whitespace characters")
        return normalized_value

    @model_validator(mode="after")
    def validate_update(self) -> "TripUpdate":
        """Reject empty, null-valued, and intrinsically invalid updates."""

        if not self.model_fields_set:
            raise ValueError("at least one field must be supplied")
        for field_name in self.model_fields_set:
            if getattr(self, field_name) is None:
                raise ValueError(f"{field_name} cannot be null")
        if self.start_date is not None and self.end_date is not None and self.end_date < self.start_date:
            raise ValueError("end_date must be on or after start_date")
        return self


class TripResponse(BaseModel):
    """Trip fields safe to return to the owning user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    source: str
    destination: str
    start_date: date
    end_date: date
    budget: Decimal
    travelers: int
    preferences: dict[str, Any]
    created_at: datetime
