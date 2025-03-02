from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import uuid
from datetime import datetime, timedelta, timezone

from models import PlayerSearch, Game, PlayerSearchCreate, PlayerSearchResponse, PlayerSearchCreateResponse
from database import get_db
from utils.errors import create_error
from fastapi import Query

router = APIRouter()


@router.post("/player_search", response_model=PlayerSearchCreateResponse)
def create_player_search(request: PlayerSearchCreate, db: Session = Depends(get_db)):
    """Erstellt ein neues Mitspieler-Gesuch."""
    
    game = db.query(Game).filter(Game.id == request.game_id).first()
    if not game:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    expires_at = datetime.now(timezone.utc) + timedelta(minutes=15)
    edit_token = str(uuid.uuid4())

    new_search = PlayerSearch(
        game_id=request.game_id,
        current_players=request.current_players,
        players_needed=request.players_needed,
        location=request.location,
        details=request.details,
        expires_at=expires_at,
        edit_token=edit_token
    )

    db.add(new_search)
    db.commit()
    db.refresh(new_search)

    return {
        **new_search.__dict__,
        "edit_token": edit_token  # Nur beim Erstellen zurückgeben
    }

@router.get("/player_search", response_model=list[PlayerSearchResponse])
def get_all_player_searches(
    db: Session = Depends(get_db),
    edit_tokens: list[str] = Query(None)  # Optionales Array von edit_tokens als Query-Parameter
):
    """Gibt alle Mitspieler-Gesuche vom aktuellen Tag zurück (mit Aktiv-Status)."""
    
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)

    # Abfragen aller Gesuche, die heute erstellt wurden
    searches = db.query(PlayerSearch).filter(
        PlayerSearch.created_at >= today_start,  # Nur heutige Gesuche
        PlayerSearch.created_at < today_end
    ).all()

    # Ergebnisliste mit dem `can_edit`-Flag für jedes Gesuch
    result = []
    for search in searches:
        # Überprüfen, ob das edit_token des Gesuchs in der Liste der edit_tokens des Benutzers enthalten ist
        can_edit = search.edit_token in edit_tokens if edit_tokens else False
        
        result.append(PlayerSearchResponse(
            id=search.id,
            game_id=search.game_id,
            current_players=search.current_players,
            players_needed=search.players_needed,
            location=search.location,
            details=search.details,  # Setze `None` wenn details leer sind (Pydantic erlaubt `None`)
            created_at=search.created_at,
            expires_at=search.expires_at,
            can_edit=can_edit,  # Flag, ob es bearbeitbar ist
            edit_token=search.edit_token if can_edit else None  # Optional, nur wenn bearbeitbar
        ))

    return result



@router.patch("/player_search/{search_id}")
def update_player_search(
    search_id: int,
    request: PlayerSearchCreate, 
    db: Session = Depends(get_db),
    edit_token: str = Query(...)
):
    """Aktualisiert ein Mitspieler-Gesuch (nur mit Token)."""
    
    search = db.query(PlayerSearch).filter(PlayerSearch.id == search_id).first()
    if not search:
        create_error(status_code=404, error_code="PAYER_SEARCH_NOT_FOUND")

    if search.edit_token != edit_token:
        create_error(status_code=403, error_code="INVALID_PAYER_SEARCH_TOKEN")

    search.current_players = request.current_players
    search.players_needed = request.players_needed
    search.location = request.location

    db.commit()
    db.refresh(search)

    return search


@router.delete("/player_search/{search_id}")
def delete_player_search(search_id: int, db: Session = Depends(get_db), edit_token: str = Query(...)):
    """Löscht ein Mitspieler-Gesuch (nur mit Token)."""
    
    search = db.query(PlayerSearch).filter(PlayerSearch.id == search_id).first()
    if not search:
        create_error(status_code=404, error_code="PAYER_SEARCH_NOT_FOUND")

    if search.edit_token != edit_token:
        create_error(status_code=403, error_code="INVALID_PAYER_SEARCH_TOKEN")

    db.delete(search)
    db.commit()

    return {"message": "Player search deleted successfully"}
