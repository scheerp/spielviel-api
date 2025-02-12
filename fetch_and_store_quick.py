import requests
import time
import html  # Import für HTML-Entescaping
from bs4 import BeautifulSoup
from typing import List, Dict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game
from helpers import assign_complexity_label
# Wir möchten parse_collection wiederverwenden
from fetch_and_store_private import parse_collection


##########################################
# 1) Funktion: fetch_collection_quick
##########################################
def fetch_collection_quick(
    username: str,
    retry_interval: int = 5,
    max_retries: int = 5
) -> str:
    """
    Holt die **öffentliche** Sammlung eines BGG-Users (kein Login, keine privaten Infos).
    Gibt **nur** das Collection-XML als String zurück.
    """
    collection_url = f"https://boardgamegeek.com/xmlapi2/collection?username={username}&stats=1"
    
    session = requests.Session()
    collection_xml = None

    for attempt in range(max_retries):
        response = session.get(collection_url)
        if response.status_code == 200 and "<message>" not in response.text:
            collection_xml = response.text
            print("✅ Öffentliche Sammlung erfolgreich abgerufen.")
            break
        else:
            print(f"⏳ Sammlung nicht bereit. Neuer Versuch in {retry_interval} Sekunden (Versuch {attempt+1}/{max_retries})")
            time.sleep(retry_interval)
    else:
        raise Exception("❌ Öffentliche Sammlung konnte nicht abgerufen werden.")

    return collection_xml


##########################################
# 2) Funktion: fetch_game_details (mit HTML-Dekodierung)
##########################################
def fetch_game_details(game_ids: List[int], max_retries=5, retry_interval=5) -> Dict[int, dict]:
    """
    Holt Detaildaten zu den angegebenen Spiel-IDs (Beschreibung, Altersangabe, Komplexität usw.).
    In Chunks von 20 IDs (Bulk).
    """
    if not game_ids:
        return {}

    details = {}
    base_url = "https://boardgamegeek.com/xmlapi2/thing"
    
    chunks = [game_ids[i:i + 20] for i in range(0, len(game_ids), 20)]

    for chunk in chunks:
        params = {"id": ",".join(map(str, chunk)), "stats": "1"}
        fetched = False
        
        for _ in range(max_retries):
            try:
                response = requests.get(base_url, params=params)
                if response.status_code == 200 and "<message>" not in response.text:
                    soup = BeautifulSoup(response.content, "lxml-xml")
                    for item in soup.find_all("item"):
                        bgg_id = int(item["id"])

                        desc_element = item.find("description")
                        unescaped_desc = html.unescape(desc_element.text) if desc_element else None  # HTML-Dekodierung

                        minage = item.find("minage")
                        averageweight = item.find("averageweight")

                        data = {
                            "description": unescaped_desc,
                            "player_age": int(minage["value"]) if minage else None,
                            "complexity": float(averageweight["value"]) if averageweight else None
                        }
                        details[bgg_id] = data

                    fetched = True
                    break
                else:
                    print(f"⏳ Warte auf Details für {chunk} ...")
                    time.sleep(retry_interval)
            except Exception as e:
                print(f"❌ Fehler bei Detailabruf für {chunk}: {e}")

        if not fetched:
            print(f"⚠️ Keine Detaildaten für IDs {chunk} (Max Retries erreicht).")

    return details


##########################################
# 3) Funktion: extract_game_ids
##########################################
def extract_game_ids(collection_xml: str) -> List[int]:
    """Parst die Collection-XML und gibt eine Liste von BGG-IDs zurück."""
    soup = BeautifulSoup(collection_xml, "lxml-xml")
    items = soup.find_all("item")
    return [int(item["objectid"]) for item in items]


##########################################
# 4) Funktion: fetch_and_store_quick (mit HTML-Dekodierung + Komplexitätslabel)
##########################################
def fetch_and_store_quick(username: str, fastMode=False):
    """
    Holt die **öffentliche** BGG-Sammlung eines Nutzers und speichert sie in der DB.

    - fastMode=False: Nur Basis-Daten (keine zusätzlichen Requests).
    - fastMode=True : *Nur für neue Spiele* Detail-Daten über Bulk-Requests.
    """
    print(f"\n📦 Starte fetch_and_store_quick für '{username}' (fastMode={fastMode})")

    try:
        # 1. Collection-XML holen (ohne Details)
        collection_xml = fetch_collection_quick(username)
        
        # 2. Collection parsen, um eine Spiele-Liste zu erhalten
        games = parse_collection(collection_xml)
        
        # 3. Wenn fastMode=True: nur für neue Spiele Detaildaten abrufen
        if fastMode:
            db: Session = SessionLocal()
            try:
                existing_games = db.query(Game).all()
                existing_ids = {eg.bgg_id for eg in existing_games}
            finally:
                db.close()

            new_ids = [g["bgg_id"] for g in games if g["bgg_id"] not in existing_ids]
            if new_ids:
                print(f"⚡ fastMode=True → Detail-Daten nur für {len(new_ids)} neue Spiele holen...")
                details = fetch_game_details(new_ids)

                for g in games:
                    bgg_id = g["bgg_id"]
                    if bgg_id in details:
                        g.update(details[bgg_id])
                        assign_complexity_label(g)
                        g["description"] = html.unescape(g["description"]) if g.get("description") else None  # HTML-Dekodierung
            else:
                print("📎 Keine neuen Spiele, daher keine zusätzlichen Detail-Requests nötig.")
        else:
            print("🐢 fastMode=False → Keine Detail-Requests, nur Basis-Daten.")

        # 4. Ab in die DB!
        result = add_games_to_db_quick(games)
        return result

    except Exception as e:
        print(f"❌ Fehler beim schnellen Abruf/Speichern: {e}")
        return {"added": 0, "updated": 0, "deleted": 0}


##########################################
# 5) Funktion: add_games_to_db_quick
##########################################
def add_games_to_db_quick(games):
    db: Session = SessionLocal()
    added_count = 0
    deleted_count = 0

    try:
        new_games_by_bgg_id = {g["bgg_id"]: g for g in games}
        existing_games = db.query(Game).all()
        existing_by_id = {eg.bgg_id: eg for eg in existing_games}

        print("\n📌 Starte 'add_games_to_db_quick'...\n")

        # 1️⃣ **Neue Spiele hinzufügen**
        for bgg_id, game_data in new_games_by_bgg_id.items():
            if bgg_id not in existing_by_id:
                # Nur Felder, die auch existieren
                game_data.pop("id", None)
                new_game = Game(**game_data)

                db.add(new_game)
                added_count += 1
                print(f"➕ Neues Spiel: {game_data['name']} (BGG {game_data['bgg_id']})")

        # 2️⃣ **Spiele entfernen, die nicht mehr in der neuen Sammlung sind**
        for existing_game in existing_games:
            if existing_game.bgg_id not in new_games_by_bgg_id:
                db.delete(existing_game)
                deleted_count += 1
                print(f"🗑️ Spiel gelöscht: {existing_game.name} (BGG {existing_game.bgg_id})")

        # 3️⃣ **Datenbank-Commit nach allen Änderungen**
        db.commit()

        print("\n✅ Verarbeitung abgeschlossen.")
        print(f"   ➕ Hinzugefügt: {added_count}")
        print(f"   🗑️ Gelöscht: {deleted_count}\n")

        return {"added": added_count, "updated": 0, "deleted": deleted_count}

    except Exception as e:
        db.rollback()
        print(f"❌ Fehler in add_games_to_db_quick: {e}")
        return {"added": 0, "updated": 0, "deleted": 0}

    finally:
        db.close()
