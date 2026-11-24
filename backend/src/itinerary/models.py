"""Persistence model for the current AI itinerary of a trip."""

from typing import Any
from uuid import UUID

from sqlalchemy import ForeignKey, Index, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from src.infrastructure.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Itinerary(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Validated AI itinerary content owned through a user's trip."""

    __tablename__ = "itineraries"
    __table_args__ = (Index("ix_itineraries_user_id_updated_at", "user_id", "updated_at"),)

    trip_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("trips.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    content: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
