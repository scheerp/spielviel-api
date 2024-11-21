import requests
import time
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game

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
    games = []
    for item in soup.find_all("item"):
        stats = item.find("stats")
        game = {
            "bgg_id": int(item["objectid"]),
            "name": item.find("name").text,
            "year_published": int(item.find("yearpublished").text) if item.find("yearpublished") else None,
            "min_players": int(stats["minplayers"]) if stats and stats.get("minplayers") else None,
            "max_players": int(stats["maxplayers"]) if stats and stats.get("maxplayers") else None,
            "min_playtime": int(stats["minplaytime"]) if stats and stats.get("minplaytime") else None,
            "max_playtime": int(stats["maxplaytime"]) if stats and stats.get("maxplaytime") else None,
            "playing_time": int(stats["playingtime"]) if stats and stats.get("playingtime") else None,
            "rating": float(item.find("average")["value"]) if item.find("average") else None,
            "img_url": item.find("image").text if item.find("image") else None,
            "thumbnail_url": item.find("thumbnail").text if item.find("thumbnail") else None,
        }
        games.append(game)
    return games


def add_games_to_db(games):
    db: Session = SessionLocal()
    try:
        for game_data in games:
            existing_game = db.query(Game).filter_by(bgg_id=game_data["bgg_id"]).first()
            if existing_game:
                for key, value in game_data.items():
                    setattr(existing_game, key, value)
            else:
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
    print(f"{len(games)} games parsed. Saving to database...")
    add_games_to_db(games)
    print("✅ Collection successfully saved to database!")
