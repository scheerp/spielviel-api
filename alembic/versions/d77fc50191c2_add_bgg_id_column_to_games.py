"""Add bgg_id column to games

Revision ID: d77fc50191c2
Revises: 
Create Date: 2024-11-16 12:43:27.556674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd77fc50191c2'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Erstelle eine neue Tabelle mit der gewünschten Struktur
    op.create_table(
        'games_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bgg_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('ean', sa.String(), nullable=True),  # Spalte 'ean' ohne NOT NULL
        sa.Column('img_url', sa.String(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Kopiere die Daten aus der alten Tabelle in die neue
    op.execute("""
        INSERT INTO games_new (id, bgg_id, name, ean, img_url, is_available)
        SELECT id, bgg_id, name, ean, img_url, is_available
        FROM games
    """)

    # Lösche die alte Tabelle
    op.drop_table('games')

    # Benenne die neue Tabelle um
    op.rename_table('games_new', 'games')

def downgrade():
    # Zurück zu der alten Struktur (falls erforderlich)
    op.create_table(
        'games_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('bgg_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('ean', sa.String(), nullable=False),  # zurück zu NOT NULL
        sa.Column('img_url', sa.String(), nullable=True),
        sa.Column('is_available', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Kopiere die Daten aus der neuen Tabelle in die alte
    op.execute("""
        INSERT INTO games_old (id, bgg_id, name, ean, img_url, is_available)
        SELECT id, bgg_id, name, ean, img_url, is_available
        FROM games
    """)

    # Lösche die neue Tabelle
    op.drop_table('games')

    # Benenne die alte Tabelle um
    op.rename_table('games_old', 'games')