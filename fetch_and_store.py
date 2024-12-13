import requests
import time
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game
from collections import defaultdict

def fetch_collection(username, retry_interval=5, max_retries=10):
    base_url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&stats=1&excludesubtype=boardgameexpansion"
    for attempt in range(max_retries):
        response = requests.get(base_url)
        if response.status_code == 200 and "<message>" not in response.text:
            return response.text
        print(f"Collection not ready yet. Retrying in {retry_interval} seconds... (Attempt {attempt + 1}/{max_retries})")
        time.sleep(retry_interval)
    raise Exception("Failed to fetch collection after multiple retries.")


def parse_collection(xml_data):
    soup = BeautifulSoup(xml_data, "lxml-xml")
    grouped_games = defaultdict(lambda: {
        "bgg_id": None,
        "name": None,
        "year_published": None,
        "min_players": None,
        "max_players": None,
        "min_playtime": None,
        "max_playtime": None,
        "playing_time": None,
        "rating": None,
        "img_url": None,
        "thumbnail_url": None,
        "available": 0,
        "total_copies": 0,
    })

    for item in soup.find_all("item"):
        bgg_id = int(item["objectid"])
        stats = item.find("stats")

        game = grouped_games[bgg_id]
        game["bgg_id"] = bgg_id
        game["name"] = item.find("name").text
        game["year_published"] = int(item.find("yearpublished").text) if item.find("yearpublished") else game["year_published"]
        game["min_players"] = int(stats["minplayers"]) if stats and stats.get("minplayers") else game["min_players"]
        game["max_players"] = int(stats["maxplayers"]) if stats and stats.get("maxplayers") else game["max_players"]
        game["min_playtime"] = int(stats["minplaytime"]) if stats and stats.get("minplaytime") else game["min_playtime"]
        game["max_playtime"] = int(stats["maxplaytime"]) if stats and stats.get("maxplaytime") else game["max_playtime"]
        game["playing_time"] = int(stats["playingtime"]) if stats and stats.get("playingtime") else game["playing_time"]
        game["rating"] = float(item.find("average")["value"]) if item.find("average") else game["rating"]
        game["img_url"] = item.find("image").text if item.find("image") else game["img_url"]
        game["thumbnail_url"] = item.find("thumbnail").text if item.find("thumbnail") else game["thumbnail_url"]
        game["available"] += 1
        game["total_copies"] += 1

    return list(grouped_games.values())


def add_games_to_db(games):
    db: Session = SessionLocal()
    try:
        new_games_by_bgg_id = {game["bgg_id"]: game for game in games}
        existing_games = db.query(Game).all()

        for existing_game in existing_games:
            if existing_game.bgg_id in new_games_by_bgg_id:
                new_data = new_games_by_bgg_id[existing_game.bgg_id]
                new_total_copies = new_data["total_copies"]

                if new_total_copies > existing_game.total_copies:
                    additional_copies = new_total_copies - existing_game.total_copies
                    print(f"Game {existing_game.name} (BGG ID: {existing_game.bgg_id}) - "
                          f"Increasing total_copies by {additional_copies}")
                    existing_game.total_copies += additional_copies
                    existing_game.available += additional_copies
                elif new_total_copies < existing_game.total_copies:
                    removed_copies = existing_game.total_copies - new_total_copies
                    print(f"Game {existing_game.name} (BGG ID: {existing_game.bgg_id}) - "
                          f"Reducing total_copies by {removed_copies}")
                    existing_game.total_copies = new_total_copies
                    existing_game.available = max(0, existing_game.available - removed_copies)
            else:
                print(f"Game {existing_game.name} (BGG ID: {existing_game.bgg_id}) no longer in XML - removing")
                db.delete(existing_game)

        for game_data in games:
            if not db.query(Game).filter_by(bgg_id=game_data["bgg_id"]).first():
                print(f"Adding new game {game_data['name']} (BGG ID: {game_data['bgg_id']})")
                new_game = Game(**game_data)
                db.add(new_game)

        db.commit()
    except Exception as e:
        print(f"Error saving to database: {e}")
        db.rollback()
    finally:
        db.close()

def fetch_and_store(username):
    print("Fetching collection data...")
    collection_xml = fetch_collection(username)
    print("Parsing collection data...")
    games = parse_collection(collection_xml)

    # Debugging-Ausgabe
    for game in games:
        print(f"Game {game['name']} (BGG ID: {game['bgg_id']}) - "
              f"Total Copies in XML: {game['total_copies']}")

    print(f"{len(games)} games parsed. Saving to database...")
    add_games_to_db(games)
    print("✅ Collection successfully updated in the database!")