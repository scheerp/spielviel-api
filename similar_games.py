from models import Game, GameSimilarity
from sqlalchemy.orm import Session
from database import SessionLocal
from random import shuffle
import logging
from typing import Dict, List, Tuple

def get_top_similar_game_ids(similar_games: List[GameSimilarity], limit: int = 6) -> List[int]:
    """
    Liefert die IDs der `limit` ähnlichsten Spiele basierend auf similarity_score,
    aber gibt sie in zufälliger Reihenfolge zurück.

    Args:
        similar_games (List[GameSimilarity]): Liste von GameSimilarity-Objekten.
        limit (int): Maximale Anzahl der zurückgegebenen IDs.

    Returns:
        List[int]: Liste der IDs der ähnlichsten Spiele (randomisiert).
    """
    # 1) Sortiere nach similarity_score DESC
    sorted_games = sorted(similar_games, key=lambda sg: sg.similarity_score, reverse=True)

    # 2) Nimm die Top-Einträge (limit)
    top_games = sorted_games[:limit]

    # 3) Shuffle das Ergebnis, damit die Rückgabe-Reihenfolge zufällig ist
    shuffle(top_games)

    # 4) Extrahiere die IDs und gib sie zurück
    return [sg.similar_game_id for sg in top_games]

    
# ------------------------------------------------------------------------------
# Logger einrichten (alternativ in main.py / __init__.py konfigurierbar)
# ------------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Falls du die Logs direkt auf der Konsole sehen möchtest:
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

# ------------------------------------------------------------------------------
# Hilfsfunktion: Ähnlichkeitsberechnung (Tags + Complexity)
# ------------------------------------------------------------------------------
def calculate_similarity(
    game_a_data: Dict,
    game_b_data: Dict
) -> Tuple[float, int, float]:
    """
    Berechnet einen Similarity-Score zwischen zwei Spielen.

    Args:
        game_a_data["tags"]: Dict[tag_id -> priority]
        game_a_data["complexity"]: float
        game_b_data["tags"]: Dict[tag_id -> priority]
        game_b_data["complexity"]: float

    Returns:
        (similarity_score, shared_tags_count, tag_priority_sum)
    """
    tags_a = game_a_data["tags"]
    tags_b = game_b_data["tags"]

    # Gemeinsame Tags
    shared_tags = set(tags_a.keys()) & set(tags_b.keys())
    shared_tags_count = len(shared_tags)
    tag_priority_sum = sum(tags_a[tag_id] + tags_b[tag_id] for tag_id in shared_tags)

    # Complexity in Score einbeziehen
    # Beispiel: Bonus, wenn Complexity-Differenz klein ist
    complexity_diff = abs(game_a_data["complexity"] - game_b_data["complexity"])
    # max Bonus 5.0, frei anpassbar
    complexity_bonus = max(0.0, 5.0 - complexity_diff)

    # Beispiel-Formel
    similarity_score = shared_tags_count + (tag_priority_sum * 0.1) + complexity_bonus

    return similarity_score, shared_tags_count, tag_priority_sum

# ------------------------------------------------------------------------------
# Hauptfunktion: Update Similarities für alle Spiele (immer alles löschen + neu)
# ------------------------------------------------------------------------------
def update_similar_games(max_similar_games: int = 10) -> int:
    """
    Aktualisiert Similarities für alle Spiele:
      1) Löscht alle Einträge in `game_similarities`.
      2) Lädt alle Spiele + Tags + Complexity in den Speicher (Variante A).
      3) Berechnet in Python (O(n^2)) alle paarweisen Similarities.
      4) Speichert pro Spiel nur die Top `max_similar_games` in der DB.
      5) Nutzt Logging und gibt die Anzahl neu erstellter Similarities zurück.

    WARNUNG: Dieses Vorgehen ist O(n^2). Bei sehr vielen Spielen kann es
             entsprechend lange dauern und RAM beanspruchen.
    """
    session = SessionLocal()
    created_count = 0

    try:
        logger.info("1) Lösche alle Einträge aus 'game_similarities' ...")
        session.query(GameSimilarity).delete()
        session.commit()
        logger.info("   -> Alle Einträge gelöscht.")

        logger.info("2) Lade alle Spiele aus der Datenbank ...")
        all_games = session.query(Game).all()
        logger.info(f"   -> {len(all_games)} Spiele geladen.")

        # Dict: game_id -> {"tags": {tag_id: priority}, "complexity": float}
        game_data = {}
        for g in all_games:
            tags_dict = {t.id: t.priority for t in g.tags} if g.tags else {}
            game_data[g.id] = {
                "tags": tags_dict,
                "complexity": g.complexity or 0.0,  # Falls None -> 0.0
            }

        # Sammelstruktur für Similarities:
        # similarities_map[game_id] = [(other_id, score, shared_tags_count, tag_priority_sum), ...]
        similarities_map = {g.id: [] for g in all_games}

        logger.info("3) Berechne Similarities in Python (O(n^2)) ...")
        game_ids = list(game_data.keys())

        for i in range(len(game_ids)):
            game_id = game_ids[i]
            for j in range(i + 1, len(game_ids)):
                other_game_id = game_ids[j]

                # Ähnlichkeit berechnen
                score, shared_tags_count, tag_priority_sum = calculate_similarity(
                    game_data[game_id],
                    game_data[other_game_id]
                )

                # Optional: Speichere nur, wenn überhaupt gemeinsame Tags
                # oder du kannst das weglassen, wenn du alles speichern möchtest
                if shared_tags_count == 0:
                    continue

                # Für beide Richtungen eintragen (game_id -> other_game_id & andersrum)
                similarities_map[game_id].append(
                    (other_game_id, score, shared_tags_count, tag_priority_sum)
                )
                similarities_map[other_game_id].append(
                    (game_id, score, shared_tags_count, tag_priority_sum)
                )

        logger.info("4) Sortiere und speichere die Top Similarities pro Spiel ...")
        for g_id, sim_list in similarities_map.items():
            if not sim_list:
                continue

            # Sortieren nach Score absteigend
            sim_list.sort(key=lambda x: x[1], reverse=True)

            # Top-Einträge (max_similar_games)
            top_entries = sim_list[:max_similar_games]

            # Neue Datensätze in DB anlegen
            for (other_id, score, shared_count, tag_sum) in top_entries:
                new_sim = GameSimilarity(
                    game_id=g_id,
                    similar_game_id=other_id,
                    similarity_score=score,
                    shared_tags_count=shared_count,
                    tag_priority_sum=tag_sum
                )
                session.add(new_sim)
                created_count += 1

        session.commit()
        logger.info("   -> Fertig! Ähnlichkeiten erfolgreich aktualisiert.")
        logger.info(f"5) Anzahl neu erstellter Similarities: {created_count}")

    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren der Similar Games: {e}")
        session.rollback()
    finally:
        session.close()

    return created_count
