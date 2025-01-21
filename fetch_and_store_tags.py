import sqlalchemy
from sqlalchemy.orm import Session
import requests
import time
from typing import List
from models import Game, Tag
from database import SessionLocal

def get_all_tags(session: Session):
    return session.query(Tag).filter(Tag.is_active == True).order_by(Tag.priority.desc()).all()


def fetch_tags_with_retry(bgg_id: int, retries: int = 3, delay: float = 2.0) -> List[str]:
    url = f"https://boardgamegeek.com/api/tags?objectid={bgg_id}&objecttype=thing"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                tags = response.json().get("globaltags", [])
                return [tag["rawtag"] for tag in tags]
        except requests.RequestException as e:
            print(f"Error fetching tags for {bgg_id} (attempt {attempt + 1}/{retries}): {e}")
        time.sleep(delay)
    print(f"Failed to fetch tags for {bgg_id} after {retries} attempts.")
    return []


def save_tags_to_db():
    session = SessionLocal()
    try:
        # Alle Tags abrufen
        all_tags = get_all_tags(session)
        games = session.query(Game).all()

        for game in games:
            print(f"Processing tags for game: {game.name}")

            # Tags abrufen und normalisieren
            raw_tags = fetch_tags_with_retry(game.bgg_id)
            normalized_tags = []

            for tag in raw_tags:
                for tag_entry in all_tags:
                    synonyms = tag_entry.synonyms.split(",") if tag_entry.synonyms else []
                    if tag.lower() in [syn.lower().strip() for syn in synonyms]:
                        normalized_tags.append(tag_entry)
                        print(f"Match found: Raw tag '{tag}' matched with '{tag_entry.normalized_tag}'")

            # Zusätzliche Regeln anwenden
            filtered_tags = []

            # Regel 1: `Duel` nur, wenn max_players ≤ 2
            for tag in normalized_tags:
                if tag.normalized_tag.lower() == "duel":
                    if game.max_players is None or game.max_players > 2:
                        print(f"Skipping tag 'Duel' for game '{game.name}' (max_players > 2)")
                        continue
                filtered_tags.append(tag)

            # Regel 2: Konflikt zwischen `Co-op` und `Competitive`
            tag_names = [tag.normalized_tag.lower() for tag in filtered_tags]
            if "co-op" in tag_names and "competitive" in tag_names:
                print(f"Conflict in game '{game.name}': Removing 'Co-op' in favor of 'Competitive'")
                filtered_tags = [tag for tag in filtered_tags if tag.normalized_tag.lower() != "co-op"]

            # Entferne Duplikate
            unique_tags = list(set(filtered_tags))

            # Existierende Tags prüfen und nur neue zuweisen
            existing_tag_ids = {tag.id for tag in game.tags}
            new_tags = [tag for tag in unique_tags if tag.id not in existing_tag_ids]

            # Tags zuweisen
            game.tags.extend(new_tags)

            print(f"Tags updated for game {game.name}: {[tag.normalized_tag for tag in game.tags]}")

        # Änderungen speichern
        session.commit()
        print("Tags updated successfully for all games.")
    except Exception as e:
        print(f"Error updating tags: {e}")
        session.rollback()
    finally:
        session.close()


def update_tags_logic():
    start_time = time.time()
    save_tags_to_db()
    print(f"Time taken to update tags: {time.time() - start_time:.2f} seconds")