"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-09

The baseline schema is materialised straight from the SQLAlchemy models so it
can never drift from them. Every migration after this one is a normal
``alembic revision --autogenerate``.
"""
from typing import Sequence, Union

from alembic import op

from app.models import Base

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
