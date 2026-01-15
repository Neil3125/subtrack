"""Add subscription_categories many-to-many table and migrate existing subscription.category_id

Revision ID: add_subscription_categories_m2m
Revises: add_activity_log_table
Create Date: 2026-01-15

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_subscription_categories_m2m'
down_revision = 'add_activity_log_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create subscription_categories association table and migrate existing data."""

    op.create_table(
        'subscription_categories',
        sa.Column('subscription_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['subscription_id'], ['subscriptions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('subscription_id', 'category_id')
    )

    # Migrate existing single category relationships into the many-to-many table
    conn = op.get_bind()
    conn.execute(sa.text("""
        INSERT INTO subscription_categories (subscription_id, category_id)
        SELECT id, category_id
        FROM subscriptions
        WHERE category_id IS NOT NULL
    """))


def downgrade() -> None:
    """Drop subscription_categories association table."""

    op.drop_table('subscription_categories')
