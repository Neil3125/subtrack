"""Add country field to customers table

Revision ID: add_country_customers
Revises: add_users_table
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_country_customers'
down_revision = 'add_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add country column to customers table
    op.add_column('customers', sa.Column('country', sa.String(100), nullable=True))
    op.create_index(op.f('ix_customers_country'), 'customers', ['country'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_customers_country'), table_name='customers')
    op.drop_column('customers', 'country')
