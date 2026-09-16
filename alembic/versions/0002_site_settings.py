"""site_settings table

Revision ID: 0002_site_settings
Revises: 0001_initial
Create Date: 2026-09-09
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_site_settings"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    # 0001_initial creates every table from the current model metadata, and
    # SiteSetting has been part of that metadata since before this revision
    # was written — so on a fresh database 0001 already created this table.
    # Guard the create so upgrading from scratch and upgrading an older,
    # pre-SiteSetting database both land in the same state.
    if not sa.inspect(bind).has_table("site_settings"):
        op.create_table(
            "site_settings",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.PrimaryKeyConstraint("id", name=op.f("pk_site_settings")),
        )


def downgrade() -> None:
    op.drop_table("site_settings")
