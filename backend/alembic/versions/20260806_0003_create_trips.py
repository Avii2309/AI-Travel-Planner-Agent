"""Create trips table.

Revision ID: 20260806_0003
Revises: 20260805_0002
Create Date: 2026-08-06 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "20260806_0003"
down_revision: str | Sequence[str] | None = "20260805_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create user-owned trip records and supporting integrity constraints."""

    op.create_table(
        "trips",
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("destination", sa.String(length=255), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("budget", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("travelers", sa.Integer(), nullable=False),
        sa.Column(
            "preferences",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.CheckConstraint("budget > 0", name=op.f("ck_trips_trip_budget_positive")),
        sa.CheckConstraint("end_date >= start_date", name=op.f("ck_trips_trip_dates_valid")),
        sa.CheckConstraint("travelers > 0", name=op.f("ck_trips_trip_travelers_positive")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], name=op.f("fk_trips_user_id_users"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_trips")),
    )
    op.create_index("ix_trips_user_id_start_date", "trips", ["user_id", "start_date"], unique=False)


def downgrade() -> None:
    """Drop trip records and their indexes."""

    op.drop_index("ix_trips_user_id_start_date", table_name="trips")
    op.drop_table("trips")
