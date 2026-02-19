import logging
import time
import requests
from typing import List, Dict, Set
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game, Tag

# ------------------------------------------------------------------------
# ✅ Logger Setup
# ------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
    logger.addHandler(console_handler)

# ------------------------------------------------------------------------
# ✅ Hilfsfunktionen
# ------------------------------------------------------------------------


def get_all_tags(session: Session) -> Dict[str, Tag]:
    """Holt alle aktiven Tags als Dictionary: { "tagname": Tag-Objekt }"""
    tags = session.query(Tag).filter(Tag.is_active.is_(True)).all()
    return {tag.normalized_tag.lower(): tag for tag in tags}


def fetch_tags_with_retry(
    bgg_id: int, retries: int = 3, delay: float = 0.5
) -> List[str]:
    """Holt Tags von BoardGameGeek mit Retry-Mechanismus."""
    url = f"https://boardgamegeek.com/api/tags?objectid={bgg_id}&objecttype=thing"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                tags = response.json().get("globaltags", [])
                return [tag["rawtag"].lower().strip() for tag in tags]
        except requests.RequestException as e:
            logger.warning(
                f"Fehler beim Abrufen der Tags für {bgg_id} "
                f"(Versuch {attempt + 1}/{retries}): {e}"
            )
        time.sleep(delay)

    logger.error(
        f"❌ Fehlgeschlagen: Keine Tags für BGG ID {bgg_id} nach {retries} Versuchen."
    )
    return []


# ------------------------------------------------------------------------
# ✅ Hauptfunktion mit `only_missing_tags` Flag
# ------------------------------------------------------------------------


def save_tags_to_db(only_missing_tags: bool = False) -> Dict[str, int]:
    """
    Aktualisiert die Tags für Spiele.

    Args:
        only_missing_tags (bool): Falls `True`, werden nur Spiele aktualisiert,
            die KEINE Tags haben.

    Returns:
        Dict mit Statistiken: {"total_games": 100, "games_updated": 20,
                              "new_tags_assigned": 50}
    """
    session = SessionLocal()
    changes = {"total_games": 0, "games_updated": 0, "new_tags_assigned": 0}

    try:
        logger.info("Lade alle Tags und Spiele aus der Datenbank...")

        # Lade alle aktiven Tags einmalig
        all_tags = get_all_tags(session)
        logger.info(f"📌 Anzahl geladener Tags aus DB: {len(all_tags)}")
        logger.info(f"📌 Tags: {list(all_tags.keys())[:10]}")  # zeige mal die ersten 10

        # Spiele-Query vorbereiten
        games_query = session.query(Game)
        if only_missing_tags:
            logger.info("🔎 Modus: Nur Spiele ohne Tags werden aktualisiert.")
            games_query = games_query.filter(
                ~Game.tags.any()
            )  # Filter: Nur Spiele ohne Tags

        # Lade alle relevanten Spiele
        games = games_query.all()
        changes["total_games"] = len(games)

        if not games:
            logger.info("✅ Keine Spiele ohne Tags gefunden. Vorgang beendet.")
            return changes

        logger.info(f"📌 Verarbeite {len(games)} Spiele...")

        for game in games:
            logger.info(f"📌 Verarbeite Spiel: {game.name} (BGG ID: {game.bgg_id})")

            # Tags abrufen
            raw_tags = fetch_tags_with_retry(game.bgg_id)
            if not raw_tags:
                continue  # Falls keine Tags gefunden -> nächstes Spiel

            # Normalisierte Tags ermitteln
            matched_tags = set()
            for raw_tag in raw_tags:
                if raw_tag in all_tags:
                    matched_tags.add(all_tags[raw_tag])
                else:
                    for tag_entry in all_tags.values():
                        synonyms = (
                            tag_entry.synonyms.split(",") if tag_entry.synonyms else []
                        )
                        if raw_tag in [syn.lower().strip() for syn in synonyms]:
                            matched_tags.add(tag_entry)
                            break

            # 🎯 Regeln anwenden
            filtered_tags = apply_tag_rules(game, matched_tags)

            # Existierende Tags ermitteln
            existing_tag_ids = {tag.id for tag in game.tags}
            new_tags = [tag for tag in filtered_tags if tag.id not in existing_tag_ids]

            if new_tags:
                game.tags.extend(new_tags)
                changes["games_updated"] += 1
                changes["new_tags_assigned"] += len(new_tags)

                logger.info(
                    f"🔹 Tags aktualisiert für '{game.name}': "
                    f" {[t.normalized_tag for t in new_tags]}"
                )

        session.commit()
        logger.info("✅ Tags für alle Spiele aktualisiert.")

    except Exception as e:
        logger.error(f"⚠️ Fehler beim Tag-Update: {e}")
        session.rollback()
    finally:
        session.close()

    return changes


# ------------------------------------------------------------------------
# ✅ Regeln für Tag-Zuordnung
# ------------------------------------------------------------------------


def apply_tag_rules(game: Game, matched_tags: Set[Tag]) -> Set[Tag]:
    """Wendet Regeln für spezielle Tags an (z. B. `Duel` nur für max 2 Spieler)."""
    filtered_tags = set(matched_tags)

    # Regel 1: `Duel` nur wenn max_players ≤ 2
    if any(t.normalized_tag.lower() == "duel" for t in filtered_tags) and (
        game.max_players is None or game.max_players > 2
    ):
        logger.info(f"❌ Entferne 'Duel' von '{game.name}' (max_players > 2)")
        filtered_tags = {t for t in filtered_tags if t.normalized_tag.lower() != "duel"}

    # Regel 2: Konflikt zwischen `Co-op` und `Competitive`
    tag_names = {t.normalized_tag.lower() for t in filtered_tags}
    if "co-op" in tag_names and "competitive" in tag_names:
        logger.info(
            f"⚠️ Konflikt: 'Co-op' und 'Competitive' bei '{game.name}'. "
            f"Entferne 'Co-op'."
        )
        filtered_tags = {
            t for t in filtered_tags if t.normalized_tag.lower() != "co-op"
        }

    return filtered_tags


# ------------------------------------------------------------------------
# ✅ Wrapper für Zeitmessung
# ------------------------------------------------------------------------


def update_tags_logic(only_missing_tags: bool = False) -> Dict[str, int]:
    """
    Führt `save_tags_to_db()` aus und misst die Laufzeit.
    """
    start_time = time.time()
    changes = save_tags_to_db(only_missing_tags=only_missing_tags)
    elapsed_time = time.time() - start_time

    logger.info(f"🚀 Tag-Update abgeschlossen in {elapsed_time:.2f} Sekunden.")
    logger.info(f"📊 Statistiken: {changes}")

    return changes
