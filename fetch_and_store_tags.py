import sqlalchemy
from sqlalchemy.orm import Session
import requests
import time
from typing import List
from models import Game
from database import SessionLocal

RELEVANT_TAGS = {
    "Co-op": ["Cooperative", "Co-op", "Coop", "Kooperativ"],
    "Strategy": ["Strategie", "Strategy", "Strat"],
    "Area-Control": ["Area Control", "Area-Control", "Area Influence", "Area-Majority", "AreaControl", "Area_Majority"],
    "Competitive": ["Competitive", "Kompetetiv", "Wettbewerb"],
    "Assymetric": ["Assymetric", "Assymetrisch", "Asymmetrisch", "Variable-Player-Powers"],
    "Miniatures": ["Miniatures", "Miniaturen", "Figures", "Figuren"],
    "Mythology": ["Mythology", "Mythologie", "Mythen"],
    "Player-Elimination": ["Player Elimination", "Player-Elimination", "Spieler-Eliminierung", "Spieler-Elimination"],
    "Egypt": ["Egypt", "Ägypten", "Ägyptisch"],
    "Tile-placement": ["Tile Placement", "Tile-Placement", "Plättchenlegen", "Plättchen-Legen","Plättchenlegespiel"],
    "Set-collection": ["Set Collection", "Set-Collection", "Kartensammlung", "Karten-Sammlung"],
    "Open-drafting": ["Open Drafting", "Open-Drafting", "Offenes Drafting", "Offenes-Drafting"],
    "Family-game": ["Familienspiel", "Family Game", "Family", "Familie"],
    "Game-of-the-year": ["Spiel des Jahres", "SdJ", "Spiel-Des-Jahres", "Spiel-des-Jahres", "spiel_des_jahres"],
    "Card-Drafting": ["Card Drafting", "Card-Drafting", "Kartendrafting", "Karten-Drafting", "Card_Drafting"],
    "Eurogame": ["Eurogame", "Euro-Game", "Euro", "Euro-Style"],
    "Tableau-Builder": ["Tableau Builder", "Tableau-Builder", "Tableau-Building", "Tableau-Building"],
    "Card-Game": ["Card Game", "Card-Game", "Kartenspiel", "Karten-Spiel", "card"],
    "Viking": ["Viking", "Vikings", "Wikinger"],
    "Fantasy": ["Fantasy", "Fantasie", "Phantasy"],
    "Kennerspiel": ["Kennerspiel", "Kennerspiel des Jahres", "Kennerspiel-des-Jahres", "Kennerspiel-des-Jahres"],
    "Ameritrash": ["Ameritrash", "Amerikatrash", "Amerika-Trash"],
    "Worker-Placement": ["Worker Placement", "Worker-Placement", "Arbeiterplatzierung", "Arbeiter-Platzierung"],
    "Deckbuilding": ["Deck Builder", "Deck-Builder", "Deckbuilding", "Deck-Building"],
    "Roll-And-Write": ["Roll and Write", "Roll-And-Write", "Roll-n-Write", "Roll-n-Write", "roll-&-write", "X-And-Write"],
    "Flip-and-write": ["Flip and Write", "Flip-and-Write", "Flip-n-Write", "Flip-n-Write", "flip-&-write"],
    "Sci-Fi": ["Sci-Fi", "Science Fiction", "Science-Fiction", "ScienceFiction"],
    "Duel": ["Duell", "Duel", "Duellspiel", "Duel Game"],
    "Modular-Board": ["Modular Board", "Modular-Board", "Modulares Spielbrett", "Modulares-Spielbrett"],
    "Zombies": ["Zombies", "Zombie", "Zombi"],
    "Push-Your-Luck": ["Push Your Luck", "Push-Your-Luck", "Push-Your-Luck-Spiel", "Push-Your-Luck-Game"],
    "Deduction": ["Deduction", "Deduktions-Spiel", "Deduktions-Spiel"],
    "EngineBuilding": ["Engine Building", "Engine-Building", "Enginebuilder", "Engine-Builder"],
    "Cthulhu": ["Cthulhu", "Cthulhu-Mythos", "Cthulhu-Mythologie"],
    "Robots": ["Robots", "Robot", "Roboter"],
    "Chaotic": ["chaotic", "chaotisch", "chaos"],
}

# Funktion zur Normalisierung von Tags
def normalize_tag(tag: str, game: Game = None) -> str:
    tag_lower = tag.lower()
    for normalized, synonyms in RELEVANT_TAGS.items():
        if tag_lower in [synonym.lower() for synonym in synonyms]:
            # Zusätzliche Logik für "Duel"
            if normalized == "Duel" and game and game.max_players > 2:
                return None
            return normalized
    return None

# Funktion zum Abrufen von Tags aus der API
def fetch_tags(bgg_id: int) -> List[str]:
    url = f"https://boardgamegeek.com/api/tags?objectid={bgg_id}&objecttype=thing"
    response = requests.get(url)
    if response.status_code == 200:
        tags = response.json().get("globaltags", [])
        return [tag["rawtag"] for tag in tags]
    return []

# Funktion zum Speichern der Tags und ähnlicher Spiele in der Datenbank
def save_tags_and_similar_games_to_db():
    session = SessionLocal()
    try:
        games = session.query(Game).all()

        for game in games:
            bgg_id = game.bgg_id

            # Tags abrufen und normalisieren
            raw_tags = fetch_tags(bgg_id)
            normalized_tags = list({normalize_tag(tag, game) for tag in raw_tags if normalize_tag(tag, game)})
            print(f"Normalized tags for {bgg_id}: {normalized_tags}")

            # Tags in die DB speichern
            game.tags = ",".join(normalized_tags) if normalized_tags else None

            # Ähnliche Spiele basierend auf Tags finden
            similar_games = find_similar_games_for_game(game, session)
            game.similar_games = ",".join(map(str, similar_games)) if similar_games else None

            session.add(game)
            time.sleep(1)  # Pause, um Blockierung zu vermeiden

        session.commit()
        print("All changes committed successfully.")
    finally:
        session.close()

# Funktion zum Ermitteln ähnlicher Spiele für ein einzelnes Spiel
def find_similar_games_for_game(game: Game, session: Session) -> List[int]:
    current_tags = set(game.tags.split(",")) if game.tags else set()
    
    if not current_tags:
        return []

    games = session.query(Game).filter(Game.id != game.id).all()
    similarity_scores = []

    for other_game in games:
        other_tags = set(other_game.tags.split(",")) if other_game.tags else set()
        common_tags = current_tags & other_tags
        similarity_scores.append((other_game.id, len(common_tags)))

    # Ähnliche Spiele nach Anzahl gemeinsamer Tags sortieren
    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    return [game_id for game_id, _ in similarity_scores[:5]]

# Hauptfunktion zur Aktualisierung der Tags und ähnlicher Spiele
def update_tags_logic():
    save_tags_and_similar_games_to_db()
