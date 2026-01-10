"""Add AI request cache table

Revision ID: add_ai_cache_table
Revises: add_saved_reports_table
Create Date: 2025-01-10

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_ai_cache_table'
down_revision = 'add_saved_reports'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create ai_request_cache table for caching AI API responses."""
    op.create_table(
        'ai_request_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('request_hash', sa.String(64), nullable=False),
        sa.Column('request_type', sa.String(50), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('response', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), default=0),
        sa.Column('hit_count', sa.Integer(), default=1),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for efficient cache lookups
    op.create_index('ix_ai_request_cache_id', 'ai_request_cache', ['id'], unique=False)
    op.create_index('ix_ai_request_cache_request_hash', 'ai_request_cache', ['request_hash'], unique=True)
    op.create_index('ix_ai_request_cache_request_type', 'ai_request_cache', ['request_type'], unique=False)
    op.create_index('ix_ai_request_cache_created_at', 'ai_request_cache', ['created_at'], unique=False)
    op.create_index('ix_ai_request_cache_expires_at', 'ai_request_cache', ['expires_at'], unique=False)
    op.create_index('idx_cache_hash_expires', 'ai_request_cache', ['request_hash', 'expires_at'], unique=False)


def downgrade() -> None:
    """Drop ai_request_cache table."""
    op.drop_index('idx_cache_hash_expires', table_name='ai_request_cache')
    op.drop_index('ix_ai_request_cache_expires_at', table_name='ai_request_cache')
    op.drop_index('ix_ai_request_cache_created_at', table_name='ai_request_cache')
    op.drop_index('ix_ai_request_cache_request_type', table_name='ai_request_cache')
    op.drop_index('ix_ai_request_cache_request_hash', table_name='ai_request_cache')
    op.drop_index('ix_ai_request_cache_id', table_name='ai_request_cache')
    op.drop_table('ai_request_cache')
