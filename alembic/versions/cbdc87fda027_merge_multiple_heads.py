"""Merge multiple heads

Revision ID: cbdc87fda027
Revises: add_activity_log_table, add_country_field, many_to_many_001, add_subscription_categories_m2m
Create Date: 2026-02-27 15:31:42.082105

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cbdc87fda027'
down_revision: Union[str, Sequence[str], None] = ('add_activity_log_table', 'add_country_field', 'many_to_many_001', 'add_subscription_categories_m2m')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
