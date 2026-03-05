"""baseline schema

Revision ID: 2c13db88e4a1
Revises:
Create Date: 2026-03-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
from database import Base
import models  # noqa: F401


# revision identifiers, used by Alembic.
revision: str = "2c13db88e4a1"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade():
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
