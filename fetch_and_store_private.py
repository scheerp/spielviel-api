import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import chromedriver_autoinstaller
import os
import json


def login_bgg(username, password):
    """
    Führt den Login bei BoardGameGeek durch und gibt eine aktive Session zurück.
    """
    login_url = "https://boardgamegeek.com/login"  # Die Login-Seite

    chromedriver_autoinstaller.install()

    # Set up Selenium WebDriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")

    # Pfad zum Chrome-Browser
    print("Chrome Binary Path:", os.getenv("CHROME_BINARY_PATH"))
    chrome_binary_path = os.getenv("CHROME_BINARY_PATH", "/usr/bin/google-chrome")
    if not os.path.exists(chrome_binary_path):
        raise FileNotFoundError(f"Chrome binary not found at {chrome_binary_path}")
    chrome_options.binary_location = chrome_binary_path

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Schritt 1: Login-Seite holen
    try:
        driver.get(login_url)
    except Exception as e:
        print(f"Fehler beim Laden der Seite: {e}")
        driver.quit()

    print("🔄 Login-Seite geladen")

    # Schritt 2: Cookie-Consent-Banner schließen
    wait = WebDriverWait(driver, 10)
    try:
        consent_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "fc-cta-do-not-consent")))
        consent_button.click()
        print("🔄 Cookie-Consent-Banner geschlossen")
    except Exception as e:
        print(f"⚠️ Kein Cookie-Consent-Banner gefunden oder Fehler beim Schließen: {e}")

    # Schritt 3: Warte, bis die Login-Felder sichtbar und interaktiv sind
    try:
        username_field = wait.until(EC.element_to_be_clickable((By.ID, "inputUsername")))
        password_field = wait.until(EC.element_to_be_clickable((By.ID, "inputPassword")))
        print("🔄 Login-Felder gefunden und interaktiv")
    except Exception as e:
        print(f"❌ Fehler beim Finden der Login-Felder: {e}")
        driver.quit()
        return None

    # Schritt 4: Login-Daten eingeben
    try:
        username_field.send_keys(username)
        password_field.send_keys(password)
        password_field.send_keys(Keys.RETURN)
        print("🔄 Login-Daten eingegeben")
    except Exception as e:
        print(f"❌ Fehler beim Eingeben der Login-Daten: {e}")
        driver.quit()
        return None

    time.sleep(1)  # Warte, bis der Login-Prozess abgeschlossen ist

    # Schritt 5: Cookies erfassen
    cookies = driver.get_cookies()
    driver.quit()

    # Cookies in ein Dictionary umwandeln
    session_cookies = {cookie['name']: cookie['value'] for cookie in cookies}

    return session_cookies


def fetch_collection(username: str, cookies: dict, retry_interval=5, max_retries=10):
    """
    Holt die XML-Daten der Sammlung eines eingeloggten Nutzers.
    """
    collection_url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&stats=1&showprivate=1"
    session = requests.Session()

    # Cookies zur Session hinzufügen
    for name, value in cookies.items():
        session.cookies.set(name, value)

    for attempt in range(max_retries):
        response = session.get(collection_url)

        if response.status_code == 200 and "<message>" not in response.text:
            print("✅ Sammlung erfolgreich abgerufen.")
            return response.text
        print(f"⏳ Sammlung noch nicht bereit. Neuer Versuch in {retry_interval} Sekunden... (Versuch {attempt + 1}/{max_retries})")
        time.sleep(retry_interval)

    raise Exception("❌ Sammlung konnte nach mehreren Versuchen nicht abgerufen werden.")

def fetch_game_descriptions(game_ids, max_retries=5, retry_interval=5):
    """
    Holt die Beschreibung (Description) von Spielen aus der BGG-API.

    Args:
        game_ids (list[int]): Eine Liste von BGG-IDs der Spiele.
        max_retries (int): Maximale Anzahl von Wiederholungen, wenn die API keine Daten liefert.
        retry_interval (int): Wartezeit (in Sekunden) zwischen den Wiederholungen.

    Returns:
        dict: Ein Dictionary mit BGG-IDs als Schlüssel und deren Description als Wert.
    """
    descriptions = {}
    base_url = "https://boardgamegeek.com/xmlapi2/thing"

    # Teile die Spiel-IDs in Gruppen von maximal 20 IDs (API-Limit pro Request)
    chunks = [game_ids[i:i + 20] for i in range(0, len(game_ids), 20)]

    for chunk in chunks:
        params = {"id": ",".join(map(str, chunk))}
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params)
                if response.status_code == 200 and "<message>" not in response.text:
                    soup = BeautifulSoup(response.content, "lxml-xml")
                    for item in soup.find_all("item"):
                        bgg_id = int(item["id"])
                        description = item.find("description").text if item.find("description") else None
                        descriptions[bgg_id] = description
                    break  # API-Request erfolgreich, nächste Chunk
                else:
                    print(f"⏳ Daten für Spiele {chunk} nicht bereit. Neuer Versuch in {retry_interval} Sekunden...")
                    time.sleep(retry_interval)
            except Exception as e:
                print(f"❌ Fehler beim Abrufen von Daten für Spiele {chunk}: {e}")
        else:
            print(f"❌ Max. Versuche überschritten für Spiele {chunk}. Übersprungen.")

    return descriptions


def parse_collection(xml_data):
    """
    Parst die XML-Daten und gibt eine Liste von Spielen zurück.
    """
    soup = BeautifulSoup(xml_data, "lxml-xml")
    grouped_games = defaultdict(lambda: {
        "bgg_id": None,
        "name": None,
        "description" : None,
        "german_description" : None,
        "year_published": None,
        "min_players": None,
        "max_players": None,
        "min_playtime": None,
        "max_playtime": None,
        "playing_time": None,
        "rating": None,
        "img_url": None,
        "thumbnail_url": None,
        "available": 1,
        "quantity": 1,
        "inventory_location": None,
        "ean": None,
        "test": None,
        "acquired_from": None,
        "private_comment": None,
    })

    for item in soup.find_all("item"):
        bgg_id = int(item["objectid"])
        stats = item.find("stats")
        private_info = item.find("privateinfo")

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

        # Parse privateinfo und privatecomment
        if private_info:
            game["available"] = int(private_info["quantity"]) if private_info and private_info.get("quantity") else game["available"]
            game["quantity"] = int(private_info["quantity"]) if private_info and private_info.get("quantity") else game["quantity"]
            game["acquired_from"] = private_info["acquiredfrom"] if private_info and private_info.get("acquiredfrom") else game["acquired_from"]
            game["inventory_location"] = private_info["inventorylocation"] if private_info and private_info.get("inventorylocation") else game["inventory_location"]
            
            private_comment = private_info.find("privatecomment")
            if private_comment is not None:
                game["private_comment"] = private_comment.text
                private_comment_text = private_comment.text.strip()
                
                if private_comment_text:
                    # Extrahiere nur den JSON-Teil nach dem Zeilenumbruch
                    json_part = private_comment_text.split("\n")[-1].strip()
                    
                    # Versuche, nur den JSON-Teil zu parsen
                    try:
                        private_comment_json = json.loads(json_part)
                        game.update(private_comment_json)
                    except json.JSONDecodeError as e:
                        print(f"⚠️ Ungültiger JSON im privatecomment: {json_part}")

    return list(grouped_games.values())

def add_games_to_db(games):
    """
    Fügt Spiele zur Datenbank hinzu oder aktualisiert vorhandene Spiele.

    Args:
        games (list[dict]): Eine Liste von Spielen mit ihren Eigenschaften.
    """
    db: Session = SessionLocal()
    try:
        # Erstelle ein Dictionary der neuen Spiele nach BGG-ID
        new_games_by_bgg_id = {game["bgg_id"]: game for game in games}

        # Hole alle existierenden Spiele aus der Datenbank
        existing_games = db.query(Game).all()
        existing_games_by_bgg_id = {game.bgg_id: game for game in existing_games}

        # Sammle alle IDs für die Description-Abfrage
        all_game_ids = list(new_games_by_bgg_id.keys())
        descriptions = fetch_game_descriptions(all_game_ids)

        # Aktualisiere existierende Spiele und füge neue Spiele hinzu
        for bgg_id, new_game_data in new_games_by_bgg_id.items():
            if bgg_id in existing_games_by_bgg_id:
                # Spiel existiert bereits, aktualisiere die Werte
                existing_game = existing_games_by_bgg_id[bgg_id]
                updated = False
                for key, value in new_game_data.items():
                    if value is not None and getattr(existing_game, key) != value:
                        setattr(existing_game, key, value)
                        updated = True
                # Aktualisiere die Description, falls vorhanden
                if bgg_id in descriptions:
                    if existing_game.description != descriptions[bgg_id]:
                        existing_game.description = descriptions[bgg_id]
                        updated = True
                if updated:
                    print(f"🔄 Spiel aktualisiert: {existing_game.name} (BGG ID: {existing_game.bgg_id})")
            else:
                # Spiel existiert noch nicht, füge es hinzu
                try:
                    new_game_data["description"] = descriptions.get(bgg_id)
                    new_game = Game(**new_game_data)
                    db.add(new_game)
                    print(f"➕ Neues Spiel hinzugefügt: {new_game_data['name']} (BGG ID: {new_game_data['bgg_id']})")
                except Exception as e:
                    print(f"❌ Fehler beim Hinzufügen eines neuen Spiels: {e}")
                    print(f"🔍 Daten des neuen Spiels: {new_game_data}")

        # Lösche Spiele, die nicht mehr in der Sammlung sind
        for bgg_id, existing_game in existing_games_by_bgg_id.items():
            if bgg_id not in new_games_by_bgg_id:
                db.delete(existing_game)
                print(f"🗑️ Spiel gelöscht: {existing_game.name} (BGG ID: {existing_game.bgg_id})")

        # Änderungen in der Datenbank speichern
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"❌ Fehler beim Hinzufügen/Aktualisieren der Spiele in der Datenbank: {e}")
    finally:
        db.close()

def fetch_and_store_private(username, password):
    print("🔒 Logging in to BoardGameGeek...")
    cookies = login_bgg(username, password)
    if not cookies:
        print("❌ Login fehlgeschlagen. Abbruch.")
        return

    print("📦 Fetching collection data...")
    collection_xml = fetch_collection(username, cookies)

    print("📊 Parsing collection data...")
    games = parse_collection(collection_xml)

    print("💾 Storing games in the database...")
    add_games_to_db(games)

    print("✅ Spiele erfolgreich abgerufen und in der Datenbank gespeichert.")

    return games