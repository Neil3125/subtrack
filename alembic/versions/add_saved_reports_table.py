"""Add saved_reports table

Revision ID: add_saved_reports
Revises: add_country_customers
Create Date: 2026-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_saved_reports'
down_revision = 'add_country_customers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create saved_reports table
    op.create_table(
        'saved_reports',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('report_type', sa.String(50), nullable=False),
        sa.Column('configuration', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_index(op.f('ix_saved_reports_id'), 'saved_reports', ['id'], unique=False)
    op.create_index(op.f('ix_saved_reports_user_id'), 'saved_reports', ['user_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_saved_reports_user_id'), table_name='saved_reports')
    op.drop_index(op.f('ix_saved_reports_id'), table_name='saved_reports')
    op.drop_table('saved_reports')
