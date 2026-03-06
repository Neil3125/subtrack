"""Add user_id to log_entries

Revision ID: 8fd04557b2c4
Revises: 46fc4d453162
Create Date: 2026-03-06 10:17:35.919870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fd04557b2c4'
down_revision: Union[str, Sequence[str], None] = '46fc4d453162'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('log_entries') as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_index('ix_log_entries_user_id', ['user_id'], unique=False)
        batch_op.create_foreign_key('fk_log_entries_users', 'users', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('log_entries') as batch_op:
        batch_op.drop_constraint('fk_log_entries_users', type_='foreignkey')
        batch_op.drop_index('ix_log_entries_user_id')
        batch_op.drop_column('user_id')
    # ### end Alembic commands ###
