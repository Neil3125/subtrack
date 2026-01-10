"""Add country field to subscriptions

Revision ID: add_country_field
Revises: add_users_table
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


# revision identifiers, used by Alembic.
revision = 'add_country_field'
down_revision = 'add_users_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Get database connection to check existing columns
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if subscriptions table exists
    tables = inspector.get_table_names()
    if 'subscriptions' not in tables:
        print("Subscriptions table does not exist yet, skipping country column")
        return
    
    columns = [col['name'] for col in inspector.get_columns('subscriptions')]
    
    # Only add column if it doesn't exist
    if 'country' not in columns:
        op.add_column('subscriptions', sa.Column('country', sa.String(100), nullable=True))
        print("Added country column to subscriptions table")
    else:
        print("Country column already exists in subscriptions table")
    
    # Check if index exists before creating
    try:
        indexes = [idx['name'] for idx in inspector.get_indexes('subscriptions')]
        if 'ix_subscriptions_country' not in indexes:
            op.create_index(op.f('ix_subscriptions_country'), 'subscriptions', ['country'], unique=False)
            print("Created index on country column")
        else:
            print("Index on country column already exists")
    except Exception as e:
        print(f"Index creation skipped: {e}")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = inspect(conn)
    
    # Check if subscriptions table exists
    tables = inspector.get_table_names()
    if 'subscriptions' not in tables:
        return
    
    # Check if index exists before dropping
    try:
        indexes = [idx['name'] for idx in inspector.get_indexes('subscriptions')]
        if 'ix_subscriptions_country' in indexes:
            op.drop_index(op.f('ix_subscriptions_country'), table_name='subscriptions')
    except Exception:
        pass
    
    # Check if column exists before dropping
    columns = [col['name'] for col in inspector.get_columns('subscriptions')]
    if 'country' in columns:
        op.drop_column('subscriptions', 'country')
