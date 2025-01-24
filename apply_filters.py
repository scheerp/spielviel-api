from sqlalchemy.orm import Query
from models import Game

# Funktion zum Anwenden von Filtern
def apply_game_filters(query: Query, filter_text: str = None, show_available_only: bool = False, min_player_count: int = 1, player_age: int = 5) -> Query:
    """
    Wendet die Filter auf die Datenbankabfrage an.

    Args:
        query (Query): Die SQLAlchemy-Abfrage.
        filter_text (str): Filter für Namen oder Beschreibung.
        show_available_only (bool): Ob nur verfügbare Spiele angezeigt werden sollen.
        min_player_count (int): Minimale Spieleranzahl.

    Returns:
        Query: Die gefilterte Abfrage.
    """
    # Filter nach Namen
    if filter_text:
        query = query.filter(Game.name.ilike(f"%{filter_text}%"))

    # Nur verfügbare Spiele
    if show_available_only:
        query = query.filter(Game.available > 0)

    # Filter nach Spieleranzahl
    query = query.filter(Game.max_players >= min_player_count)
    
    # Filter nach Spieleralter
    query = query.filter(Game.player_age >= player_age)

    return query
