import requests
import time
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game
from scrape_german_name_playwright import get_german_name_with_playwright

# Schritt 1: Daten von der BGG-API holen
def fetch_geeklist(bgg_list_id, retry_interval=5, max_retries=10):
    """
    Fetches a geeklist from BoardGameGeek API, waiting if the request is queued.
    """
    base_url = f"https://boardgamegeek.com/xmlapi/geeklist/{bgg_list_id}"
    for attempt in range(max_retries):
        response = requests.get(base_url)
        if response.status_code == 200 and "<message>" not in response.text:
            return response.text
        print(f"Geeklist not ready yet. Retrying in {retry_interval} seconds...")
        time.sleep(retry_interval)
    raise Exception("Failed to fetch geeklist after multiple retries.")


# Schritt 3: Einträge in die Datenbank hinzufügen
def add_entries_to_db(data):
    db: Session = SessionLocal()
    try:
        for entry in data:
            game = Game(
                bgg_id=entry["bgg_id"],
                name=entry["name"],
                img_url=entry["img_url"],
                ean="",  # Initially empty
                is_available=True
            )
            existing_game = db.query(Game).filter_by(bgg_id=game.bgg_id).first()
            if not existing_game:
                db.add(game)
        db.commit()
    except Exception as e:
        print(f"Fehler beim Hinzufügen von Einträgen: {e}")
        db.rollback()
    finally:
        db.close()

# Hauptprozess
def main():
    bgg_list_id = 346629  # Beispiel-Geeeklist-ID
    bgg_base_url = "https://boardgamegeek.com"

    print("Fetching Geeklist...")
    geeklist_xml = fetch_geeklist(bgg_list_id)

    print("Parsing Geeklist...")
    soup = BeautifulSoup(geeklist_xml, "lxml-xml")  # Sicherstellen, dass der XML-Parser verwendet wird
    items = soup.find_all("item")

    print(f"{len(items)} Spiele gefunden. Starte Verarbeitung...")

    scraped_data = []
    for item in items:
        object_id = int(item["objectid"])
        object_name = item["objectname"]
        print(f"Processing Game ID: {object_id} - {object_name}")

        # Scrape German name and image
        scraped_info = get_german_name_with_playwright(bgg_base_url, object_id)
        german_name = scraped_info["title"] or object_name
        img_url = scraped_info["img_url"]

        # Add to the dataset
        scraped_data.append({
            "bgg_id": object_id,
            "name": german_name,
            "img_url": img_url
        })

        # Rate limiting to avoid being blocked
        time.sleep(2)

    print("Speichere Daten in der Datenbank...")
    add_entries_to_db(scraped_data)
    print("Alle Daten erfolgreich gespeichert!")

# Skript starten
if __name__ == "__main__":
    main()
