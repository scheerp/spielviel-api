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
        # Alle Tags einmal abrufen
        all_tags = get_all_tags(session)
        games = session.query(Game).all()

        for game in games:
            print(f"Processing tags for game: {game.name}")

            # Tags abrufen und normalisieren
            raw_tags = fetch_tags_with_retry(game.bgg_id)
            normalized_tags = [
                tag_entry for tag in raw_tags
                for tag_entry in all_tags
                if tag.lower() in (syn.lower() for syn in (tag_entry.synonyms.split(",") if tag_entry.synonyms else []))
            ]

            # Existierende Tags entfernen und neue zuweisen
            game.tags.clear()
            for tag in set(normalized_tags):
                game.tags.append(tag)

            print(f"Tags updated for game {game.name}: {[tag.normalized_tag for tag in game.tags]}")

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