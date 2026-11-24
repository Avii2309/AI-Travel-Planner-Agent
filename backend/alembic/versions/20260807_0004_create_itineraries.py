"""Create persisted AI itineraries.

Revision ID: 20260807_0004
Revises: 20260806_0003
Create Date: 2026-08-07 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "20260807_0004"
down_revision: str | Sequence[str] | None = "20260806_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create one current validated itinerary per user-owned trip."""

    op.create_table(
        "itineraries",
        sa.Column("trip_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("content", postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["trip_id"], ["trips.id"], name=op.f("fk_itineraries_trip_id_trips"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_itineraries_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_itineraries")),
        sa.UniqueConstraint("trip_id", name=op.f("uq_itineraries_trip_id")),
    )
    op.create_index("ix_itineraries_user_id_updated_at", "itineraries", ["user_id", "updated_at"], unique=False)


def downgrade() -> None:
    """Drop persisted itinerary records."""

    op.drop_index("ix_itineraries_user_id_updated_at", table_name="itineraries")
    op.drop_table("itineraries")
