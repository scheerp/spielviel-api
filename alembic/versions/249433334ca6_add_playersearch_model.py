"""Add PlayerSearch model

Revision ID: 249433334ca6
Revises: be19b8f8e835
Create Date: 2025-03-02 12:12:18.780822

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '249433334ca6'
down_revision: Union[str, None] = 'be19b8f8e835'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('player_search',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=False),
    sa.Column('current_players', sa.Integer(), nullable=False),
    sa.Column('players_needed', sa.Integer(), nullable=False),
    sa.Column('location', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('edit_token', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('edit_token')
    )
    op.create_index(op.f('ix_player_search_id'), 'player_search', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_player_search_id'), table_name='player_search')
    op.drop_table('player_search')
    # ### end Alembic commands ###
