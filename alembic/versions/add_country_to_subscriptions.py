"""Add country field to subscriptions

Revision ID: add_country_field
Revises: add_users_table
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_country_field'
down_revision = 'add_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add country column to subscriptions table
    op.add_column('subscriptions', sa.Column('country', sa.String(100), nullable=True, index=True))
    op.create_index(op.f('ix_subscriptions_country'), 'subscriptions', ['country'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_subscriptions_country'), table_name='subscriptions')
    op.drop_column('subscriptions', 'country')
