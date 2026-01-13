"""Add renewal notices table

Revision ID: add_renewal_notices
Revises: add_saved_reports_table
Create Date: 2026-01-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_renewal_notices'
down_revision = 'add_saved_reports_table'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'renewal_notices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('recipient_email', sa.String(255), nullable=True),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('success', sa.Boolean(), default=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('notice_type', sa.String(50), nullable=False, default='manual'),
        sa.Column('renewal_date_at_send', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_renewal_notices_subscription_id', 'renewal_notices', ['subscription_id'])
    op.create_index('ix_renewal_notices_customer_id', 'renewal_notices', ['customer_id'])
    op.create_index('ix_renewal_notices_sent_at', 'renewal_notices', ['sent_at'])


def downgrade():
    op.drop_index('ix_renewal_notices_sent_at', table_name='renewal_notices')
    op.drop_index('ix_renewal_notices_customer_id', table_name='renewal_notices')
    op.drop_index('ix_renewal_notices_subscription_id', table_name='renewal_notices')
    op.drop_table('renewal_notices')
