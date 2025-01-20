from typing import List, Tuple
from models import Game, GameSimilarity
from sqlalchemy.orm import Session
from database import SessionLocal
from random import shuffle

def get_top_similar_game_ids(similar_games: List[GameSimilarity], limit: int = 6) -> List[int]:
    """
    Liefert die IDs der `limit` ähnlichsten Spiele basierend auf similarity_score.
    Bei gleicher similarity_score werden Spiele zufällig gemischt.

    Args:
        similar_games (List[GameSimilarity]): Liste von GameSimilarity-Objekten.
        limit (int): Maximale Anzahl der zurückgegebenen IDs.

    Returns:
        List[int]: Liste der IDs der ähnlichsten Spiele.
    """
    # Gruppiere die Spiele nach similarity_score
    similar_game_groups = {}
    for sg in similar_games:
        similar_game_groups.setdefault(sg.similarity_score, []).append(sg.similar_game_id)

    # Sortiere die Gruppen nach similarity_score absteigend
    top_similar_ids = []
    for similarity_score in sorted(similar_game_groups.keys(), reverse=True):
        candidates = similar_game_groups[similarity_score]
        shuffle(candidates)  # Zufällige Reihenfolge innerhalb der Gruppe
        top_similar_ids.extend(candidates)

        if len(top_similar_ids) >= limit:  # Stoppe, wenn das Limit erreicht ist
            break

    # Beschränke die Liste auf maximal `limit` IDs
    return top_similar_ids[:limit]

def find_similar_games_for_game(game: Game, session: Session, limit: int = 10) -> List[Tuple[int, float, int, float]]:
    """
    Findet bis zu `limit` ähnliche Spiele basierend auf geteilten Tags.
    Gibt eine Liste von Tupeln zurück: (similar_game_id, similarity_score, shared_tags_count, tag_priority_sum).
    """
    current_tags = {tag.id: tag.priority for tag in game.tags} if game.tags else {}

    if not current_tags:
        return []

    games = session.query(Game).filter(Game.id != game.id).all()
    similarity_scores = []

    for other_game in games:
        other_tags = {tag.id: tag.priority for tag in other_game.tags} if other_game.tags else {}

        # Gemeinsame Tags und Metriken berechnen
        shared_tags = set(current_tags.keys()) & set(other_tags.keys())
        shared_tags_count = len(shared_tags)
        tag_priority_sum = sum(current_tags[tag_id] + other_tags[tag_id] for tag_id in shared_tags)
        similarity_score = shared_tags_count + (tag_priority_sum * 0.1)  # Gewichtung für die Priorität

        if shared_tags_count > 0:
            similarity_scores.append((other_game.id, similarity_score, shared_tags_count, tag_priority_sum))

    # Sortieren: Ähnlichkeitswert (absteigend), dann ID (aufsteigend)
    similarity_scores.sort(key=lambda x: (-x[1], x[0]))

    # Begrenzen auf die Top `limit` Ergebnisse
    return similarity_scores[:limit]


def update_similar_games(max_similar_games: int = 10):
    """
    Aktualisiert die Ähnlichkeit zwischen allen Spielen und speichert die Ergebnisse in der Tabelle `game_similarities`.
    Begrenze die Anzahl ähnlicher Spiele pro Spiel auf `max_similar_games`.
    """
    session = SessionLocal()
    try:
        # Bestehende Einträge löschen (falls vorhanden)
        session.query(GameSimilarity).delete()

        games = session.query(Game).all()

        for game in games:
            print(f"Updating similar games for {game.name}")

            # Finde ähnliche Spiele (begrenzt auf `max_similar_games`)
            similar_games_with_scores = find_similar_games_for_game(game, session, limit=max_similar_games)

            # Speichere Ähnlichkeiten in der Datenbank
            for similar_game_id, score, shared_tags_count, tag_priority_sum in similar_games_with_scores:
                similarity_entry = GameSimilarity(
                    game_id=game.id,
                    similar_game_id=similar_game_id,
                    similarity_score=score,
                    shared_tags_count=shared_tags_count,
                    tag_priority_sum=tag_priority_sum,
                )
                session.add(similarity_entry)

        session.commit()
        print(f"Similar games updated for all games (limited to {max_similar_games} per game).")
    except Exception as e:
        print(f"Error updating similar games: {e}")
        session.rollback()
    finally:
        session.close()