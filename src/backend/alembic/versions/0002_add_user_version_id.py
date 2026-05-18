"""add users.version_id

Revision ID: 0002
Revises: 0001
Create Date: 2026-05-18

"""
from __future__ import annotations

from typing import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        table_name="users",
        column=sa.Column("version_id", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column(table_name="users", column_name="version_id")
