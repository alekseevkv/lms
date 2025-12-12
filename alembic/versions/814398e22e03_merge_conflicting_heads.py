"""Merge conflicting heads

Revision ID: 814398e22e03
Revises: abe1ea162bfd, c014f0b1de40
Create Date: 2025-12-05 22:39:55.651050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '814398e22e03'
down_revision: Union[str, Sequence[str], None] = ('abe1ea162bfd', 'c014f0b1de40')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
