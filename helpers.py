from sqlalchemy import or_, and_
from typing import List, Optional
from sqlalchemy.orm import Query
from models import Game

# 🔹 Mapping für Complexity-Kategorien
COMPLEXITY_MAPPING = [
    {"label": "Family", "min": 0.9, "max": 1.5},
    {"label": "Beginner", "min": 1.5, "max": 2.2},
    {"label": "Intermediate", "min": 2.2, "max": 3},
    {"label": "Advanced", "min": 3, "max": 4},
    {"label": "", "min": 4, "max": 5},
]

def get_complexity_label(complexity: float) -> str:
    """Gibt das Complexity-Label für einen gegebenen Complexity-Wert zurück."""
    if complexity is None:
        return None
    for category in COMPLEXITY_MAPPING:
        if category["min"] < complexity <= category["max"]:
            return category["label"]
    return None

def assign_complexity_label(game):
    """Setzt das Complexity-Label eines Spiels basierend auf seinem Complexity-Wert."""
    game["complexity_label"] = get_complexity_label(game.get("complexity"))


# 🔹 Filter-Funktion für die Spiele-Datenbankabfrage
def apply_game_filters(
    query: Query, 
    filter_text: Optional[str] = None, 
    show_available_only: bool = False, 
    min_player_count: int = 1, 
    player_age: int = 5, 
    show_missing_ean_only: bool = False,
    complexities: Optional[List[str]] = None
) -> Query:
    """
    Applies various filters to the database query.

    Args:
        query (Query): The SQLAlchemy query.
        filter_text (Optional[str]): Filter for name or description.
        show_available_only (bool): If True, only available games are shown.
        min_player_count (int): Minimum number of players required.
        player_age (int): Minimum recommended player age.
        show_missing_ean_only (bool): If True, only games without an EAN are shown.
        complexities (Optional[List[str]]): List of complexity labels (e.g., ["Beginner", "Expert"]).

    Returns:
        Query: The filtered query.
    """

    # 🔹 Filter by name
    if filter_text:
        query = query.filter(Game.name.ilike(f"%{filter_text}%"))

    # 🔹 Show only available games
    if show_available_only:
        query = query.filter(Game.available > 0)

    # 🔹 Filter by player count
    query = query.filter(Game.max_players >= min_player_count)

    # 🔹 Filter by player age
    query = query.filter(Game.player_age >= player_age)

    # 🔹 Show only games without EAN
    if show_missing_ean_only:
        query = query.filter(Game.ean.is_(None))

    # 🔹 Apply Complexity Filter
    if complexities:
        query = query.filter(Game.complexity_label.in_(complexities))

    return query
