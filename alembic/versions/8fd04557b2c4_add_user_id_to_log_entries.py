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
    bind = op.get_bind()
    if bind.engine.name == 'postgresql':
        op.execute("ALTER TABLE log_entries ADD COLUMN IF NOT EXISTS user_id INTEGER")
        op.execute("CREATE INDEX IF NOT EXISTS ix_log_entries_user_id ON log_entries (user_id)")
        
        # Check if foreign key exists before adding
        engine = sa.create_engine(bind.engine.url)
        with engine.connect() as conn:
            res = conn.execute(sa.text(
                "SELECT conname FROM pg_constraint WHERE conname = 'fk_log_entries_users'"
            )).fetchone()
            if not res:
                op.execute(
                    "ALTER TABLE log_entries ADD CONSTRAINT fk_log_entries_users "
                    "FOREIGN KEY(user_id) REFERENCES users(id)"
                )
    else:
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
