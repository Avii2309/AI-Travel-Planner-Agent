"""Initial database layer revision.

Revision ID: 20260805_0001
Revises:
Create Date: 2026-08-05 00:00:00

The application deliberately has no domain models at this stage, so this
revision establishes Alembic versioning without creating business tables.
"""

from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "20260805_0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the initial schema (currently empty by design)."""


def downgrade() -> None:
    """Revert the initial schema (currently empty by design)."""
