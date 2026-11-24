"""Persist Google Places verification for trip destinations.

Revision ID: 20261119_0005
Revises: 20260807_0004
Create Date: 2026-11-19 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261119_0005"
down_revision: str | Sequence[str] | None = "20260807_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add nullable Google Places details to preserve existing trip rows."""

    op.add_column("trips", sa.Column("destination_place_id", sa.String(length=255), nullable=True))
    op.add_column("trips", sa.Column("destination_name", sa.String(length=255), nullable=True))
    op.add_column("trips", sa.Column("destination_address", sa.String(length=512), nullable=True))
    op.add_column("trips", sa.Column("destination_latitude", sa.Float(), nullable=True))
    op.add_column("trips", sa.Column("destination_longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove Google Places destination details."""

    op.drop_column("trips", "destination_longitude")
    op.drop_column("trips", "destination_latitude")
    op.drop_column("trips", "destination_address")
    op.drop_column("trips", "destination_name")
    op.drop_column("trips", "destination_place_id")
