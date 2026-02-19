import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Game
from utils.filters import assign_complexity_label
import os
import json
import html
from typing import List, Dict

api_token = os.environ["BGG_API_TOKEN"]

# Token als Authorization Header setzen
headers = {"Authorization": f"Bearer {api_token}", "User-Agent": "SpielViel-App/1.0"}


def fetch_collection(
    username: str, cookies: dict = None, retry_interval=5, max_retries=10
):
    """
    Holt die XML-Daten der Sammlung eines Nutzers unter Verwendung des API-Tokens.
    Cookies werden nicht mehr benötigt, Token reicht.
    """
    collection_url = (
        f"https://boardgamegeek.com/xmlapi2/collection?"
        f"username={username}&stats=1&showprivate=1"
    )
    session = requests.Session()

    for attempt in range(max_retries):
        response = session.get(collection_url, headers=headers)

        if response.status_code == 200 and "<message>" not in response.text:
            print("✅ Sammlung erfolgreich abgerufen.")
            return response.text

        print(
            f"⏳ Sammlung noch nicht bereit. "
            f"Neuer Versuch in {retry_interval} Sekunden... "
            f"(Versuch {attempt + 1}/{max_retries})"
        )
        time.sleep(retry_interval)

    raise Exception(
        "❌ Sammlung konnte nach mehreren Versuchen nicht abgerufen werden."
    )


def fetch_game_details(
    game_ids: List[int], max_retries=5, retry_interval=5
) -> Dict[int, dict]:
    """
    Holt die Details von Spielen aus der BGG-API,
    einschließlich Beschreibung, Altersangabe, Komplexität
    und empfohlene Spieleranzahl.

    Hier wird zusätzlich die Beschreibung (sofern vorhanden)
    mit html.unescape() in echte Zeichen konvertiert.
    """
    details = {}
    base_url = "https://boardgamegeek.com/xmlapi2/thing"

    # Teile die Spiel-IDs in Gruppen von maximal 20 IDs (API-Limit pro Request)
    chunks = [game_ids[i : i + 20] for i in range(0, len(game_ids), 20)]

    for chunk in chunks:
        params = {"id": ",".join(map(str, chunk)), "stats": "1"}
        for attempt in range(max_retries):
            try:
                response = requests.get(base_url, params=params, headers=headers)
                if response.status_code == 200 and "<message>" not in response.text:
                    soup = BeautifulSoup(response.content, "lxml-xml")
                    for item in soup.find_all("item"):
                        bgg_id = int(item["id"])

                        # Beschreibung auslesen und HTML-Entities decodieren
                        desc_element = item.find("description")
                        raw_desc = desc_element.text if desc_element else None
                        unescaped_desc = html.unescape(raw_desc) if raw_desc else None

                        data = {
                            "description": unescaped_desc,  # Beschreibung dekodiert
                            "player_age": parse_safe_int(item.find("minage"), "value"),
                            "complexity": parse_safe_float(
                                item.find("averageweight"), "value"
                            ),
                            "best_playercount": None,
                            "min_recommended_playercount": None,
                            "max_recommended_playercount": None,
                        }

                        # Empfohlene Spieleranzahl
                        poll = item.find("poll", {"name": "suggested_numplayers"})
                        if poll:
                            results = poll.find_all("results")
                            best_playercount = parse_best_playercount(results)
                            if best_playercount is not None:
                                data["best_playercount"] = best_playercount

                            recommended_players = parse_recommended_players(results)
                            if recommended_players:
                                data["min_recommended_playercount"] = min(
                                    recommended_players
                                )
                                data["max_recommended_playercount"] = max(
                                    recommended_players
                                )

                        details[bgg_id] = data
                    break
                else:
                    print(
                        f"⏳ Daten für Spiele {chunk} nicht bereit. "
                        f"Neuer Versuch in {retry_interval} Sekunden..."
                    )
                    time.sleep(retry_interval)
            except Exception as e:
                print(f"❌ Fehler beim Abrufen von Daten für Spiele {chunk}: {e}")
        else:
            print(f"❌ Max. Versuche überschritten für Spiele {chunk}. Übersprungen.")

    return details


def parse_safe_int(element, attribute):
    """
    Sicheres Parsen eines Integer-Werts aus einem XML-Element.
    """
    if element and element.has_attr(attribute):
        value = element[attribute]
        try:
            return int(value.replace("+", "").strip())  # Entferne '+' und Leerzeichen
        except ValueError:
            print(f"⚠️ Fehler beim Parsen von int: '{value}'")
    return None


def parse_safe_float(element, attribute):
    """
    Sicheres Parsen eines Float-Werts aus einem XML-Element.
    """
    if element and element.has_attr(attribute):
        value = element[attribute]
        try:
            return float(value.strip())
        except ValueError:
            print(f"⚠️ Fehler beim Parsen von float: '{value}'")
    return None


def parse_best_playercount(results):
    """
    Bestimme die empfohlene Spieleranzahl basierend auf den meisten Stimmen für "Best".
    """
    try:
        best_result = max(
            results,
            key=lambda r: int(r.find("result", {"value": "Best"})["numvotes"]),
            default=None,
        )
        if best_result:
            return parse_safe_int(best_result, "numplayers")
    except Exception as e:
        print(f"⚠️ Fehler beim Bestimmen der empfohlenen Spieleranzahl: {e}")
    return None


def parse_recommended_players(results):
    """
    Extrahiere die Liste der empfohlenen Spieleranzahlen basierend auf "Recommended".
    """
    recommended = []
    for r in results:
        try:
            if r.find("result", {"value": "Recommended"}):
                numplayers = parse_safe_int(r, "numplayers")
                if numplayers is not None:
                    recommended.append(numplayers)
        except Exception as e:
            print(f"⚠️ Fehler beim Extrahieren der empfohlenen Spieleranzahlen: {e}")
    return recommended


def parse_collection(xml_data):
    """
    Parst die XML-Daten und gibt eine Liste von Spielen zurück.
    """
    soup = BeautifulSoup(xml_data, "lxml-xml")
    grouped_games = defaultdict(
        lambda: {
            "bgg_id": None,
            "name": None,
            "description": None,
            "german_description": None,
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
            "acquired_from": None,
            "private_comment": None,
            "player_age": None,
            "complexity": None,
            "best_playercount": None,
            "min_recommended_playercount": None,
            "max_recommended_playercount": None,
        }
    )

    for item in soup.find_all("item"):
        bgg_id = int(item["objectid"])
        stats = item.find("stats")
        private_info = item.find("privateinfo")

        game = grouped_games[bgg_id]
        game["bgg_id"] = bgg_id
        game["name"] = item.find("name").text
        game["year_published"] = (
            int(item.find("yearpublished").text)
            if item.find("yearpublished")
            else game["year_published"]
        )
        game["min_players"] = (
            int(stats["minplayers"])
            if stats and stats.get("minplayers")
            else game["min_players"]
        )
        game["max_players"] = (
            int(stats["maxplayers"])
            if stats and stats.get("maxplayers")
            else game["max_players"]
        )
        game["min_playtime"] = (
            int(stats["minplaytime"])
            if stats and stats.get("minplaytime")
            else game["min_playtime"]
        )
        game["max_playtime"] = (
            int(stats["maxplaytime"])
            if stats and stats.get("maxplaytime")
            else game["max_playtime"]
        )
        game["playing_time"] = (
            int(stats["playingtime"])
            if stats and stats.get("playingtime")
            else game["playing_time"]
        )
        game["rating"] = (
            float(item.find("average")["value"])
            if item.find("average")
            else game["rating"]
        )
        game["img_url"] = (
            item.find("image").text if item.find("image") else game["img_url"]
        )
        game["thumbnail_url"] = (
            item.find("thumbnail").text
            if item.find("thumbnail")
            else game["thumbnail_url"]
        )

        # Parse privateinfo und privatecomment
        if private_info:
            game["available"] = (
                int(private_info["quantity"])
                if private_info and private_info.get("quantity")
                else game["available"]
            )
            game["quantity"] = (
                int(private_info["quantity"])
                if private_info and private_info.get("quantity")
                else game["quantity"]
            )
            game["acquired_from"] = (
                private_info["acquiredfrom"]
                if private_info and private_info.get("acquiredfrom")
                else game["acquired_from"]
            )
            game["inventory_location"] = (
                private_info["inventorylocation"]
                if private_info and private_info.get("inventorylocation")
                else game["inventory_location"]
            )

            private_comment = private_info.find("privatecomment")
            if private_comment is not None:
                game["private_comment"] = private_comment.text
                private_comment_text = private_comment.text.strip()

                if private_comment_text:
                    # Extrahiere nur den JSON-Teil nach dem Zeilenumbruch
                    json_part = private_comment_text.split("\n")[-1].strip()

                    try:
                        private_comment_json = json.loads(json_part)
                        game.update(private_comment_json)
                    except json.JSONDecodeError:
                        print(f"⚠️ Ungültiger JSON im privatecomment: {json_part}")

    return list(grouped_games.values())


def add_games_to_db(games):
    db: Session = SessionLocal()
    added_count = 0
    updated_count = 0
    deleted_count = 0

    try:
        new_games_by_bgg_id = {game["bgg_id"]: game for game in games}

        # Alle existierenden Spiele aus der DB abrufen
        existing_games = db.query(Game).all()
        existing_games_by_bgg_id = {game.bgg_id: game for game in existing_games}

        all_game_ids = list(new_games_by_bgg_id.keys())
        details = fetch_game_details(all_game_ids)

        for bgg_id, new_game_data in new_games_by_bgg_id.items():
            if bgg_id in details:
                new_game_data.update(details[bgg_id])

            assign_complexity_label(new_game_data)

            if bgg_id in existing_games_by_bgg_id:
                existing_game = existing_games_by_bgg_id[bgg_id]
                updated = False

                for key, value in new_game_data.items():
                    if (
                        key != "id"
                        and value is not None
                        and getattr(existing_game, key) != value
                    ):
                        setattr(existing_game, key, value)
                        updated = True

                if updated:
                    updated_count += 1
                    print(
                        f"🔄 Spiel aktualisiert: {existing_game.name} "
                        f"(BGG ID: {existing_game.bgg_id})"
                    )
            else:
                try:
                    new_game_data.pop("id", None)
                    new_game = Game(**new_game_data)
                    db.add(new_game)
                    added_count += 1
                    print(
                        f"➕ Neues Spiel hinzugefügt: "
                        f"{new_game_data['name']} "
                        f"(BGG ID: {new_game_data['bgg_id']})"
                    )
                except Exception as e:
                    print(f"❌ Fehler beim Hinzufügen eines neuen Spiels: {e}")

        # Lösche Spiele, die nicht mehr in der aktuellen Sammlung enthalten sind
        for existing_game in existing_games:
            if existing_game.bgg_id not in new_games_by_bgg_id:
                db.delete(existing_game)
                deleted_count += 1
                print(
                    f"🗑️ Spiel gelöscht: {existing_game.name} "
                    f"(BGG ID: {existing_game.bgg_id})"
                )

        db.commit()
        return {
            "added": added_count,
            "updated": updated_count,
            "deleted": deleted_count,
        }

    except Exception as e:
        db.rollback()
        print(f"❌ Fehler beim Aktualisieren der Datenbank: {e}")
        return {"added": 0, "updated": 0, "deleted": 0}

    finally:
        db.close()


def fetch_and_store_private(username, password=None):
    print("📦 Fetching collection data...")
    collection_xml = fetch_collection(username)

    print("📊 Parsing collection data...")
    games = parse_collection(collection_xml)

    print("💾 Storing games in the database...")
    result = add_games_to_db(games)

    print("✅ Spiele erfolgreich abgerufen und in der Datenbank gespeichert.")
    return result  # Gibt jetzt eine Statistik zurück
