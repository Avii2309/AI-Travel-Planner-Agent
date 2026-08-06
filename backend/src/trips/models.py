"""Trip persistence model."""

from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, Numeric, String, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Trip(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A user-owned trip planning record."""

    __tablename__ = "trips"
    __table_args__ = (
        CheckConstraint("end_date >= start_date", name="trip_dates_valid"),
        CheckConstraint("budget > 0", name="trip_budget_positive"),
        CheckConstraint("travelers > 0", name="trip_travelers_positive"),
        Index("ix_trips_user_id_start_date", "user_id", "start_date"),
    )

    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    travelers: Mapped[int] = mapped_column(nullable=False)
    preferences: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default=text("'{}'::jsonb"),
    )
