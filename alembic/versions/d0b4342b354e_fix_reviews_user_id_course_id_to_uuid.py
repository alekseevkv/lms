"""fix reviews user_id course_id to uuid

Revision ID: d0b4342b354e
Revises: ab4b851696c2
Create Date: 2025-12-13 01:47:06.956537

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd0b4342b354e'
down_revision: Union[str, Sequence[str], None] = 'ab4b851696c2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("reviews")

    op.create_table(
        "reviews",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("create_at", sa.DateTime(), nullable=False),
        sa.Column("update_at", sa.DateTime(), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),

        sa.PrimaryKeyConstraint("uuid"),

        sa.ForeignKeyConstraint(["user_id"], ["users.uuid"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.uuid"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    op.drop_table("reviews")

    op.create_table(
        "reviews",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("course_id", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("uuid", sa.UUID(), nullable=False),
        sa.Column("create_at", sa.DateTime(), nullable=False),
        sa.Column("update_at", sa.DateTime(), nullable=False),
        sa.Column("archived", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("uuid"),
    )

