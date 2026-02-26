"""remove expires_at from player_search

Revision ID: 19655d3d41fd
Revises: 830e9e63e6a5
Create Date: 2026-02-25 08:21:57.515718

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "19655d3d41fd"
down_revision: Union[str, None] = "830e9e63e6a5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column("player_search", "expires_at")


def downgrade():
    op.add_column(
        "player_search",
        sa.Column("expires_at", sa.DateTime(), nullable=True),
    )
