"""Remove profile_picture column from User

Revision ID: 29b41b64989a
Revises: aee95ebff110
Create Date: 2025-02-01 20:04:12.864551

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '29b41b64989a'
down_revision: Union[str, None] = 'aee95ebff110'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_picture')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_picture', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
