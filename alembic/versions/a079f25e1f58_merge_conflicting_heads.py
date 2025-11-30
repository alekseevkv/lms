"""Merge conflicting heads

Revision ID: a079f25e1f58
Revises: d5a7411748f0, eb518cf31643
Create Date: 2025-11-30 14:56:46.128039

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a079f25e1f58'
down_revision: Union[str, Sequence[str], None] = ('d5a7411748f0', 'eb518cf31643')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
