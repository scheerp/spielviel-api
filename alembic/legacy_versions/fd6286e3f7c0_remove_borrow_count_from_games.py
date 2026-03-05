"""remove borrow_count from games

Revision ID: fd6286e3f7c0
Revises: 19655d3d41fd
Create Date: 2026-03-01 11:21:29.599781

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fd6286e3f7c0"
down_revision: Union[str, None] = "19655d3d41fd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column("games", "borrow_count")


def downgrade():
    op.add_column("games", sa.Column("borrow_count", sa.Integer(), nullable=True))
