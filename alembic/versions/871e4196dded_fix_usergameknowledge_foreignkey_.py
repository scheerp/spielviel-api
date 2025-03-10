"""Fix UserGameKnowledge ForeignKey constraint

Revision ID: 871e4196dded
Revises: cdcf2ff80ead
Create Date: 2025-03-10 17:47:15.807291

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '871e4196dded'
down_revision: Union[str, None] = 'cdcf2ff80ead'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 1. Lösche den alten ForeignKey, falls vorhanden
    op.drop_constraint('user_game_knowledge_game_id_fkey', 'user_game_knowledge', type_='foreignkey')

    # 2. Erstelle den neuen ForeignKey mit ON DELETE CASCADE
    op.create_foreign_key(
        'user_game_knowledge_game_id_fkey',  # Name des ForeignKeys
        'user_game_knowledge',  # Tabelle, in der sich die Spalte befindet
        'games',  # Tabelle, auf die verwiesen wird
        ['game_id'],  # Spalte in user_game_knowledge
        ['id'],  # Spalte in games
        ondelete="CASCADE"  # Stellt sicher, dass beim Löschen eines Spiels auch die Knowledge-Daten gelöscht werden
    )

def downgrade():
    # Rückgängig machen der Änderung (falls nötig)
    op.drop_constraint('user_game_knowledge_game_id_fkey', 'user_game_knowledge', type_='foreignkey')
    op.create_foreign_key(
        'user_game_knowledge_game_id_fkey',
        'user_game_knowledge',
        'games',
        ['game_id'],
        ['id']
    )