"""Persist Geoapify verification for trip starting locations.

Revision ID: 20261119_0006
Revises: 20261119_0005
Create Date: 2026-11-19 00:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "20261119_0006"
down_revision: str | Sequence[str] | None = "20261119_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add nullable starting-location details without changing existing trips."""

    op.add_column("trips", sa.Column("source_place_id", sa.String(length=255), nullable=True))
    op.add_column("trips", sa.Column("source_name", sa.String(length=255), nullable=True))
    op.add_column("trips", sa.Column("source_address", sa.String(length=512), nullable=True))
    op.add_column("trips", sa.Column("source_latitude", sa.Float(), nullable=True))
    op.add_column("trips", sa.Column("source_longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove starting-location verification details."""

    op.drop_column("trips", "source_longitude")
    op.drop_column("trips", "source_latitude")
    op.drop_column("trips", "source_address")
    op.drop_column("trips", "source_name")
    op.drop_column("trips", "source_place_id")
