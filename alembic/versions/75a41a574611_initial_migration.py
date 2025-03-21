"""Initial migration

Revision ID: 75a41a574611
Revises: 
Create Date: 2025-02-01 19:52:40.310171

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision: str = '75a41a574611'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # ### commands auto generated by Alembic - adjusted for dependencies ###

    # Foreign Key Constraints verhindern, dass Tabellen einfach gelöscht werden
    # -> Wir müssen erst `game_tags` entfernen, bevor `tags` gelöscht wird

    op.execute("DROP TABLE game_tags CASCADE")
    op.execute("DROP TABLE game_similarities CASCADE")
    op.execute("DROP TABLE tags CASCADE")
    op.execute("DROP TABLE games CASCADE")
    op.execute("DROP TABLE users CASCADE")

    # Falls Indexe entfernt werden müssen
    op.drop_index('ix_tags_german_normalized_tag', table_name='tags', if_exists=True)
    op.drop_index('ix_tags_id', table_name='tags', if_exists=True)
    op.drop_index('ix_tags_normalized_tag', table_name='tags', if_exists=True)
    op.drop_index('ix_users_id', table_name='users', if_exists=True)
    op.drop_index('ix_users_username', table_name='users', if_exists=True)
    op.drop_index('ix_game_similarities_game_id', table_name='game_similarities', if_exists=True)
    op.drop_index('ix_game_similarities_id', table_name='game_similarities', if_exists=True)
    op.drop_index('ix_game_similarities_similar_game_id', table_name='game_similarities', if_exists=True)
    op.drop_index('ix_games_bgg_id', table_name='games', if_exists=True)
    op.drop_index('ix_games_id', table_name='games', if_exists=True)
    op.drop_index('ix_games_name', table_name='games', if_exists=True)

    # ### end Alembic commands ###

def downgrade() -> None:
    # ### commands auto generated by Alembic ###
    op.create_table('tags',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('normalized_tag', sa.VARCHAR(), nullable=False),
    sa.Column('german_normalized_tag', sa.VARCHAR(), nullable=False),
    sa.Column('synonyms', sa.VARCHAR(), nullable=True),
    sa.Column('priority', sa.INTEGER(), nullable=True),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='tags_pkey')
    )
    op.create_index('ix_tags_normalized_tag', 'tags', ['normalized_tag'], unique=True)
    op.create_index('ix_tags_id', 'tags', ['id'], unique=False)
    op.create_index('ix_tags_german_normalized_tag', 'tags', ['german_normalized_tag'], unique=True)

    op.create_table('users',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', sa.VARCHAR(), nullable=False),
    sa.Column('hashed_password', sa.VARCHAR(), nullable=False),
    sa.Column('is_active', sa.BOOLEAN(), nullable=True),
    sa.Column('role', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey')
    )
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_index('ix_users_id', 'users', ['id'], unique=False)

    op.create_table('games',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('bgg_id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(), nullable=False),
    sa.Column('description', sa.VARCHAR(), nullable=True),
    sa.Column('german_description', sa.VARCHAR(), nullable=True),
    sa.Column('year_published', sa.INTEGER(), nullable=True),
    sa.Column('min_players', sa.INTEGER(), nullable=True),
    sa.Column('max_players', sa.INTEGER(), nullable=True),
    sa.Column('min_playtime', sa.INTEGER(), nullable=True),
    sa.Column('max_playtime', sa.INTEGER(), nullable=True),
    sa.Column('playing_time', sa.INTEGER(), nullable=True),
    sa.Column('rating', sa.DOUBLE_PRECISION(precision=53), nullable=True),
    sa.Column('ean', sa.INTEGER(), nullable=True),
    sa.Column('available', sa.INTEGER(), nullable=True),
    sa.Column('borrow_count', sa.INTEGER(), nullable=True),
    sa.Column('quantity', sa.INTEGER(), nullable=True),
    sa.Column('acquired_from', sa.VARCHAR(), nullable=True),
    sa.Column('inventory_location', sa.VARCHAR(), nullable=True),
    sa.Column('private_comment', sa.VARCHAR(), nullable=True),
    sa.Column('img_url', sa.VARCHAR(), nullable=True),
    sa.Column('thumbnail_url', sa.VARCHAR(), nullable=True),
    sa.Column('player_age', sa.INTEGER(), nullable=True),
    sa.Column('complexity', sa.DOUBLE_PRECISION(precision=53), nullable=True),
    sa.Column('best_playercount', sa.INTEGER(), nullable=True),
    sa.Column('min_recommended_playercount', sa.INTEGER(), nullable=True),
    sa.Column('max_recommended_playercount', sa.INTEGER(), nullable=True),
    sa.PrimaryKeyConstraint('id', name='games_pkey'),
    sa.UniqueConstraint('ean', name='games_ean_key')
    )
    op.create_index('ix_games_name', 'games', ['name'], unique=False)
    op.create_index('ix_games_id', 'games', ['id'], unique=False)
    op.create_index('ix_games_bgg_id', 'games', ['bgg_id'], unique=False)

    op.create_table('game_similarities',
    sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('game_id', sa.INTEGER(), nullable=False),
    sa.Column('similar_game_id', sa.INTEGER(), nullable=False),
    sa.Column('similarity_score', sa.DOUBLE_PRECISION(precision=53), nullable=False),
    sa.Column('shared_tags_count', sa.INTEGER(), nullable=False),
    sa.Column('tag_priority_sum', sa.DOUBLE_PRECISION(precision=53), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], name='game_similarities_game_id_fkey'),
    sa.ForeignKeyConstraint(['similar_game_id'], ['games.id'], name='game_similarities_similar_game_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='game_similarities_pkey')
    )
    op.create_index('ix_game_similarities_similar_game_id', 'game_similarities', ['similar_game_id'], unique=False)
    op.create_index('ix_game_similarities_id', 'game_similarities', ['id'], unique=False)
    op.create_index('ix_game_similarities_game_id', 'game_similarities', ['game_id'], unique=False)

    op.create_table('game_tags',
    sa.Column('game_id', sa.INTEGER(), nullable=False),
    sa.Column('tag_id', sa.INTEGER(), nullable=False),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], name='game_tags_game_id_fkey'),
    sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], name='game_tags_tag_id_fkey'),
    sa.PrimaryKeyConstraint('game_id', 'tag_id', name='game_tags_pkey')
    )

    # ### end Alembic commands ###
