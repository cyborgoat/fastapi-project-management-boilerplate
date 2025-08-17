"""Fix is_admin and is_superuser default values

Revision ID: f18e61171b93
Revises: 4e5237800a34
Create Date: 2025-08-17 16:29:25.336378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f18e61171b93'
down_revision: Union[str, Sequence[str], None] = '4e5237800a34'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # First, update all NULL values to False for both columns
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE \"user\" SET is_admin = false WHERE is_admin IS NULL"))
    connection.execute(sa.text("UPDATE \"user\" SET is_superuser = false WHERE is_superuser IS NULL"))
    
    # Now alter the columns to be non-nullable with defaults
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('is_admin', nullable=False, server_default='false')
        batch_op.alter_column('is_superuser', nullable=False, server_default='false')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert to nullable columns
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('is_admin', nullable=True, server_default=None)
        batch_op.alter_column('is_superuser', nullable=True, server_default=None)
