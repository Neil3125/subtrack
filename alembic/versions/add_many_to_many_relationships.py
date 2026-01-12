"""Add many-to-many relationships for customers

Revision ID: many_to_many_001
Revises: 
Create Date: 2026-01-12 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'many_to_many_001'
down_revision = None  # Set this to your latest revision
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create association tables and migrate existing data."""
    
    # Create customer_categories association table
    op.create_table(
        'customer_categories',
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('customer_id', 'category_id')
    )
    
    # Create customer_groups association table
    op.create_table(
        'customer_groups',
        sa.Column('customer_id', sa.Integer(), nullable=False),
        sa.Column('group_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('customer_id', 'group_id')
    )
    
    # Migrate existing data from customers table to association tables
    # This will copy existing category_id and group_id to the new many-to-many tables
    conn = op.get_bind()
    
    # Migrate category relationships
    conn.execute(sa.text("""
        INSERT INTO customer_categories (customer_id, category_id)
        SELECT id, category_id
        FROM customers
        WHERE category_id IS NOT NULL
    """))
    
    # Migrate group relationships
    conn.execute(sa.text("""
        INSERT INTO customer_groups (customer_id, group_id)
        SELECT id, group_id
        FROM customers
        WHERE group_id IS NOT NULL
    """))
    
    # Make category_id nullable (keeping for backward compatibility)
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('category_id',
                              existing_type=sa.Integer(),
                              nullable=True)
        # Make country required
        batch_op.alter_column('country',
                              existing_type=sa.String(100),
                              nullable=False)


def downgrade() -> None:
    """Remove association tables and restore single relationships."""
    
    # Restore single category/group per customer (take first one from many-to-many)
    conn = op.get_bind()
    
    # Restore category_id from first category in many-to-many
    conn.execute(sa.text("""
        UPDATE customers
        SET category_id = (
            SELECT category_id
            FROM customer_categories
            WHERE customer_categories.customer_id = customers.id
            LIMIT 1
        )
        WHERE category_id IS NULL
    """))
    
    # Restore group_id from first group in many-to-many
    conn.execute(sa.text("""
        UPDATE customers
        SET group_id = (
            SELECT group_id
            FROM customer_groups
            WHERE customer_groups.customer_id = customers.id
            LIMIT 1
        )
        WHERE group_id IS NULL
    """))
    
    # Drop association tables
    op.drop_table('customer_groups')
    op.drop_table('customer_categories')
    
    # Make category_id required again
    with op.batch_alter_table('customers', schema=None) as batch_op:
        batch_op.alter_column('category_id',
                              existing_type=sa.Integer(),
                              nullable=False)
        # Make country optional again
        batch_op.alter_column('country',
                              existing_type=sa.String(100),
                              nullable=True)
