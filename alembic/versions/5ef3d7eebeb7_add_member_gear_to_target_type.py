"""add member_gear to target_type

Revision ID: 5ef3d7eebeb7
Revises: b235442fb49a
Create Date: 2026-09-11 05:44:23.885608

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ef3d7eebeb7'
down_revision: Union[str, Sequence[str], None] = 'b235442fb49a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE targettype ADD VALUE IF NOT EXISTS 'member_gear'")


def downgrade() -> None:
    """Downgrade schema."""
    # PostgreSQLはEnum値の削除を直接サポートしていないため、downgradeは実装しない
    pass