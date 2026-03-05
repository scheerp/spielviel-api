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


def _build_virtual_game(target_type: str, target_complexity_label: str | None) -> dict:
    if target_type == "complexity":
        label = target_complexity_label or "Unbekannt"
        return {
            "id": None,
            "name": f"Komplexität: {label}",
            "min_players": None,
            "max_players": None,
            "min_playtime": None,
            "max_playtime": None,
            "complexity_label": label,
            "img_url": None,
            "thumbnail_url": None,
            "best_playercount": None,
            "player_age": None,
        }

    return {
        "id": None,
        "name": "Freie Suche",
        "min_players": None,
        "max_players": None,
        "min_playtime": None,
        "max_playtime": None,
        "complexity_label": None,
        "img_url": None,
        "thumbnail_url": None,
        "best_playercount": None,
        "player_age": None,
    }


@router.get("/", response_model=list[dict])
def get_all_player_searches(
    db: Session = Depends(get_db),
    expire_after_minutes: int = Query(15, ge=1),
    edit_tokens: list[str] = Query(
        None
    ),  # Optionales Array von edit_tokens als Query-Parameter
):
    """Gibt alle Mitspieler-Gesuche vom aktuellen Tag zurück, gruppiert nach Spiel."""

    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)
    valid_after = now - timedelta(minutes=expire_after_minutes)

    # Alle heutigen PlayerSearch-Objekte abrufen
    searches = (
        db.query(PlayerSearch)
        .filter(
            PlayerSearch.created_at >= today_start, PlayerSearch.created_at < today_end
        )
        .all()
    )

    # Alle benötigten Spiele auf einmal abrufen (statt in einer Schleife)
    game_ids = {search.game_id for search in searches if search.game_id is not None}
    games = db.query(Game).filter(Game.id.in_(game_ids)).all()
    game_dict = {game.id: game for game in games}  # Mapping für schnelleren Zugriff

    # Ergebnisse gruppieren
    grouped_results = defaultdict(lambda: {"game": None, "player_searches": []})

    for search in searches:
        target_type = search.target_type or "game"

        if target_type == "game":
            game = game_dict.get(search.game_id)
            if not game:
                continue
            group_key = search.game_id
            game_payload = {
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
        elif target_type == "complexity":
            label = search.target_complexity_label or "Unbekannt"
            group_key = f"complexity:{label}"
            game_payload = _build_virtual_game("complexity", label)
        else:
            group_key = "free"
            game_payload = _build_virtual_game("free", None)

        if grouped_results[group_key]["game"] is None:
            grouped_results[group_key]["game"] = game_payload

        # Überprüfen, ob das edit_token des Gesuchs in der Liste der edit_tokens ist
        can_edit = search.edit_token in edit_tokens if edit_tokens else False

        # Gesuch hinzufügen
        grouped_results[group_key]["player_searches"].append(
            {
                "id": search.id,
                "game_id": search.game_id,
                "target_type": target_type,
                "target_complexity_label": search.target_complexity_label,
                "name": search.name,
                "current_players": search.current_players,
                "players_needed": search.players_needed,
                "location": search.location,
                "details": search.details,
                "created_at": search.created_at,
                "is_valid": search.created_at >= valid_after,
                "can_edit": can_edit,
                "edit_token": search.edit_token if can_edit else None,
            }
        )

    return list(grouped_results.values())


@router.get("/public")
def get_valid_player_searches(
    db: Session = Depends(get_db),
    expire_after_minutes: int = Query(15, ge=1),
):
    """
    Public endpoint für Displays.
    Gibt nur valide Player Searches zurück (keine Auth, keine edit_tokens).
    """

    now = datetime.now(timezone.utc)

    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)

    valid_after = now - timedelta(minutes=expire_after_minutes)

    searches = (
        db.query(PlayerSearch)
        .filter(
            PlayerSearch.created_at >= today_start,
            PlayerSearch.created_at < today_end,
            PlayerSearch.created_at >= valid_after,
        )
        .all()
    )

    game_ids = {search.game_id for search in searches if search.game_id is not None}
    games = db.query(Game).filter(Game.id.in_(game_ids)).all()
    game_dict = {game.id: game for game in games}

    grouped_results = defaultdict(lambda: {"game": None, "player_searches": []})

    for search in searches:
        target_type = search.target_type or "game"

        if target_type == "game":
            game = game_dict.get(search.game_id)
            if not game:
                continue
            group_key = search.game_id
            game_payload = {
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
        elif target_type == "complexity":
            label = search.target_complexity_label or "Unbekannt"
            group_key = f"complexity:{label}"
            game_payload = _build_virtual_game("complexity", label)
        else:
            group_key = "free"
            game_payload = _build_virtual_game("free", None)

        if grouped_results[group_key]["game"] is None:
            grouped_results[group_key]["game"] = game_payload

        grouped_results[group_key]["player_searches"].append(
            {
                "id": search.id,
                "game_id": search.game_id,
                "target_type": target_type,
                "target_complexity_label": search.target_complexity_label,
                "name": search.name,
                "current_players": search.current_players,
                "players_needed": search.players_needed,
                "location": search.location,
                "details": search.details,
                "created_at": search.created_at,
            }
        )

    return {
        "generated_at": now,
        "count": len(searches),
        "data": list(grouped_results.values()),
    }


@router.post("/create", response_model=PlayerSearchCreateResponse)
def create_player_search(request: PlayerSearchCreate, db: Session = Depends(get_db)):
    """Erstellt ein neues Mitspieler-Gesuch."""

    target_type = request.target_type
    game_id = request.game_id
    target_complexity_label = (
        request.target_complexity_label.strip()
        if request.target_complexity_label is not None
        else None
    )

    if target_type == "game":
        if game_id is None:
            create_error(
                status_code=400,
                error_code="INTERNAL_ERROR",
                detailed_message="game_id is required for target_type=game",
            )
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            create_error(status_code=404, error_code="GAME_NOT_FOUND")
        target_complexity_label = None
    elif target_type == "complexity":
        if not target_complexity_label:
            create_error(
                status_code=400,
                error_code="INTERNAL_ERROR",
                detailed_message=(
                    "target_complexity_label is required " "for target_type=complexity"
                ),
            )
        game_id = None
    elif target_type == "free":
        game_id = None
        target_complexity_label = None
    else:
        create_error(
            status_code=400,
            error_code="INTERNAL_ERROR",
            detailed_message="target_type must be one of: game, complexity, free",
        )

    edit_token = str(uuid.uuid4())
    details = request.details if request.details is not None else None

    new_search = PlayerSearch(
        game_id=game_id,
        target_type=target_type,
        target_complexity_label=target_complexity_label,
        current_players=request.current_players,
        name=request.name,
        players_needed=request.players_needed,
        location=request.location,
        details=details,
        edit_token=edit_token,
    )

    db.add(new_search)
    db.commit()
    db.refresh(new_search)

    return {
        "id": new_search.id,
        "game_id": new_search.game_id,
        "target_type": new_search.target_type,
        "target_complexity_label": new_search.target_complexity_label,
        "name": new_search.name,
        "current_players": new_search.current_players,
        "players_needed": new_search.players_needed,
        "location": new_search.location,
        "details": new_search.details,
        "edit_token": new_search.edit_token,
        "created_at": new_search.created_at,
    }


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

    target_type = request.target_type
    game_id = request.game_id
    target_complexity_label = (
        request.target_complexity_label.strip()
        if request.target_complexity_label is not None
        else None
    )

    if target_type == "game":
        if game_id is None and search.game_id is not None:
            game_id = search.game_id
        if game_id is None:
            create_error(
                status_code=400,
                error_code="INTERNAL_ERROR",
                detailed_message="game_id is required for target_type=game",
            )
        game = db.query(Game).filter(Game.id == game_id).first()
        if not game:
            create_error(status_code=404, error_code="GAME_NOT_FOUND")
        target_complexity_label = None
    elif target_type == "complexity":
        if not target_complexity_label:
            create_error(
                status_code=400,
                error_code="INTERNAL_ERROR",
                detailed_message=(
                    "target_complexity_label is required " "for target_type=complexity"
                ),
            )
        game_id = None
    elif target_type == "free":
        game_id = None
        target_complexity_label = None
    else:
        create_error(
            status_code=400,
            error_code="INTERNAL_ERROR",
            detailed_message="target_type must be one of: game, complexity, free",
        )

    search.game_id = game_id
    search.target_type = target_type
    search.target_complexity_label = target_complexity_label
    search.current_players = request.current_players
    search.players_needed = request.players_needed
    search.name = request.name
    search.location = request.location
    search.details = request.details
    search.edit_token = request.edit_token

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
