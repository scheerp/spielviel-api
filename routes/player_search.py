from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from models import (
    PlayerSearch,
    Game,
    PlayerSearchCreate,
    PlayerSearchEdit,
    PlayerSearchCreateResponse,
)
from database import get_db
from utils.errors import create_error
from fastapi import Query

router = APIRouter()


@router.get("/", response_model=list[dict])
def get_all_player_searches(
    db: Session = Depends(get_db),
    edit_tokens: list[str] = Query(
        None
    ),  # Optionales Array von edit_tokens als Query-Parameter
):
    """Gibt alle Mitspieler-Gesuche vom aktuellen Tag zurück, gruppiert nach Spiel."""

    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)

    # Alle heutigen PlayerSearch-Objekte abrufen
    searches = (
        db.query(PlayerSearch)
        .filter(
            PlayerSearch.created_at >= today_start, PlayerSearch.created_at < today_end
        )
        .all()
    )

    # Alle benötigten Spiele auf einmal abrufen (statt in einer Schleife)
    game_ids = {search.game_id for search in searches}
    games = db.query(Game).filter(Game.id.in_(game_ids)).all()
    game_dict = {game.id: game for game in games}  # Mapping für schnelleren Zugriff

    # Ergebnisse gruppieren
    grouped_results = defaultdict(lambda: {"game": None, "player_searches": []})

    for search in searches:
        game = game_dict.get(search.game_id)
        if not game:
            continue  # Falls kein passendes Spiel gefunden wird

        # Falls das Spiel noch nicht in den Ergebnissen ist, hinzufügen
        if grouped_results[search.game_id]["game"] is None:
            grouped_results[search.game_id]["game"] = {
                "id": game.id,
                "name": game.name,
                "min_players": game.min_players,
                "max_players": game.max_players,
                "min_playtime": game.min_playtime,
                "max_playtime": game.max_playtime,
                "complexity_label": game.complexity_label,
                "img_url": game.img_url,
                "thumbnail_url": game.thumbnail_url,
                "best_playercount": game.best_playercount,
                "player_age": game.player_age,
            }

        # Überprüfen, ob das edit_token des Gesuchs in der Liste der edit_tokens ist
        can_edit = search.edit_token in edit_tokens if edit_tokens else False

        # Gesuch hinzufügen
        grouped_results[search.game_id]["player_searches"].append(
            {
                "id": search.id,
                "name": search.name,
                "current_players": search.current_players,
                "players_needed": search.players_needed,
                "location": search.location,
                "details": search.details,
                "created_at": search.created_at,
                "expires_at": search.expires_at,
                "can_edit": can_edit,
                "edit_token": search.edit_token if can_edit else None,
            }
        )

    return list(grouped_results.values())


@router.post("/create", response_model=PlayerSearchCreateResponse)
def create_player_search(request: PlayerSearchCreate, db: Session = Depends(get_db)):
    """Erstellt ein neues Mitspieler-Gesuch."""

    game = db.query(Game).filter(Game.id == request.game_id).first()
    if not game:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    edit_token = str(uuid.uuid4())
    details = request.details if request.details is not None else None

    new_search = PlayerSearch(
        game_id=request.game_id,
        current_players=request.current_players,
        name=request.name,
        players_needed=request.players_needed,
        location=request.location,
        details=details,
        expires_at=expires_at,
        edit_token=edit_token,
    )

    db.add(new_search)
    db.commit()
    db.refresh(new_search)

    return {**new_search.__dict__, "edit_token": edit_token}


@router.patch("/update/{search_id}")
def update_player_search(
    search_id: int,
    request: PlayerSearchEdit,
    db: Session = Depends(get_db),
):
    """Aktualisiert ein Mitspieler-Gesuch (nur mit Token)."""

    search = db.query(PlayerSearch).filter(PlayerSearch.id == search_id).first()
    if not search:
        create_error(status_code=404, error_code="PAYER_SEARCH_NOT_FOUND")

    if search.edit_token != request.edit_token:
        create_error(status_code=403, error_code="INVALID_PAYER_SEARCH_TOKEN")

    search.current_players = request.current_players
    search.players_needed = request.players_needed
    search.name = request.name
    search.location = request.location
    search.edit_token = request.edit_token
    search.can_edit = True

    db.commit()
    db.refresh(search)

    return search


@router.delete("/{search_id}")
def delete_player_search(
    search_id: int, db: Session = Depends(get_db), edit_token: str = Query(...)
):
    """Löscht ein Mitspieler-Gesuch (nur mit Token)."""

    search = db.query(PlayerSearch).filter(PlayerSearch.id == search_id).first()
    if not search:
        create_error(status_code=404, error_code="PAYER_SEARCH_NOT_FOUND")

    if search.edit_token != edit_token:
        create_error(status_code=403, error_code="INVALID_PAYER_SEARCH_TOKEN")

    db.delete(search)
    db.commit()

    return {"message": "Player search deleted successfully"}
