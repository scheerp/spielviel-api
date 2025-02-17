from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc
from database import get_db
from models import Game, GameResponse, GamesWithCountResponse, GameResponseWithDetails, User, AddEANRequest
from utils.filters import apply_game_filters
from typing import List
from similar_games import get_top_similar_game_ids
from utils.errors import create_error
from auth import require_role

router = APIRouter()

@router.get("/", response_model=GamesWithCountResponse)
def read_all_games(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    filter_text: str = Query(None),
    show_available_only: bool = Query(False),
    min_player_count: int = Query(1, ge=1),
    player_age: int = Query(5, ge=0),
    show_missing_ean_only: bool = Query(False),
    complexities: list[str] = Query(None, description="Liste von Complexity-Labels (z.B. ?complexities=einsteiger&complexities=fortgeschritten)")
):
    query = db.query(Game).options(joinedload(Game.tags)).order_by(asc(Game.name))
    query = apply_game_filters(query, filter_text, show_available_only, min_player_count, player_age, show_missing_ean_only, complexities)
    total_games = query.count()
    games = query.offset(offset).limit(limit).all()

    return {"games": games, "total": total_games}


@router.get("/count")
def get_games_count(
    db: Session = Depends(get_db),
    filter_text: str = Query(None, description="Filter nach Namen"),
    show_available_only: bool = Query(False, description="Nur verfügbare Spiele anzeigen"),
    min_player_count: int = Query(1, ge=1, description="Minimale Spieleranzahl"),
    player_age: int = Query(5, ge=0, description="Minimales Alter der Spieler"),
    show_missing_ean_only: bool = Query(False, description="Nur Spiele ohne ean anzeigen"),
    complexities: list[str] = Query(None, description="Liste von Complexity-Labels (z.B. ?complexities=einsteiger&complexities=fortgeschritten)")
):
    """
    Gibt die Gesamtanzahl der Spiele basierend auf den aktuellen Filtern zurück.
    """
    query = db.query(Game)
    query = apply_game_filters(query,filter_text, show_available_only, min_player_count, player_age, show_missing_ean_only, complexities)
    total_count = query.count()

    return {"total_count": total_count}


@router.get("/game/{game_id}", response_model=GameResponseWithDetails)
def read_game(game_id: int, db: Session = Depends(get_db)):
    game = (
        db.query(Game)
        .options(joinedload(Game.tags), joinedload(Game.similar_games))
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": top_similar_ids
    }

@router.get("/borrowed-games", response_model=GamesWithCountResponse)
def read_borrowed_games(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper"))
):
    query = db.query(Game).options(joinedload(Game.tags)).filter(Game.borrow_count > 0).order_by(asc(Game.name))
    total_games = query.count()
    games = query.all()

    return {"games": games, "total": total_games}

@router.post("/by-ids", response_model=List[GameResponse])
def read_games_by_ids(game_ids: List[int], db: Session = Depends(get_db)):
    games = db.query(Game).options(joinedload(Game.tags)).filter(Game.id.in_(game_ids)).all()
    if not games:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE", details={"game_ids": game_ids})
    return games


@router.get("/game/by_ean/{ean}", response_model=GameResponse)
def read_game_by_ean(ean: str, db: Session = Depends(get_db)):
    game = db.query(Game).options(joinedload(Game.tags)).filter(Game.ean == ean).first()
    if not game:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"ean": ean})
    return game


@router.put("/game/borrow/{game_id}")
def borrow_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # Spiel abrufen
    game = db.query(Game).options(joinedload(Game.similar_games)).filter(Game.id == game_id).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"game_id": game_id})

    # Verfügbarkeit prüfen und aktualisieren
    if game.available > 0:
        game.available -= 1
        game.borrow_count += 1
    else:
        create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")

    db.commit()
    db.refresh(game)

    # Ähnliche Spiele berechnen
    # top_similar_ids = get_top_similar_game_ids(game.similar_games)

    # Rückgabe des aktualisierten Spiels mit ähnlichen Spielen
    return {
        **game.__dict__,
        "tags": game.tags,
        # "similar_games": top_similar_ids  # IDs der 5 ähnlichsten Spiele
    }

@router.put("/game/return/{game_id}")
def return_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # Spiel abrufen
    game = db.query(Game).options(joinedload(Game.similar_games)).filter(Game.id == game_id).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"game_id": game_id})

    # Verfügbarkeit prüfen und aktualisieren
    if game.available < game.quantity:
        game.available += 1
    else:
        create_error(status_code=400, error_code="ALL_COPIES_AVAILABLE")
        game.available = game.quantity

    db.commit()
    db.refresh(game)
    

    # Ähnliche Spiele berechnen
    # top_similar_ids = get_top_similar_game_ids(game.similar_games)

    # Rückgabe des aktualisierten Spiels mit ähnlichen Spielen
    return {
        **game.__dict__,
        "tags": game.tags,
        # "similar_games": top_similar_ids  # IDs der 5 ähnlichsten Spiele
    }

@router.put("/game/add_ean/{game_id}")
def add_ean(game_id: int, request: AddEANRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("helper"))):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"game_id": game_id})

    existing_game = db.query(Game).filter(Game.ean == request.ean).first()
    if existing_game:
        create_error(
            status_code=409,
            error_code="BARCODE_CONFLICT",
            details={
                "id": existing_game.id,
                "name": existing_game.name,
                "ean": existing_game.ean,
                "thumbnail_url": existing_game.thumbnail_url
            },
        )
    game.ean = request.ean
    db.commit()
    db.refresh(game)

    return game

@router.put("/game/remove_ean/{game_id}")
def remove_ean(game_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_role("admin"))):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"game_id": game_id})

    game.ean = None
    db.commit()
    db.refresh(game)

    return game

@router.put("/game/borrow_by_ean/{game_ean}")
def borrow_game_ean(game_ean: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("helper"))):
    game = db.query(Game).filter(Game.ean == game_ean).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"ean": game_ean})
    if game.available > 0:
        game.available -= 1
        game.borrow_count += 1
    else:
        create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")
    db.commit()
    db.refresh(game)
    return game


@router.put("/game/return_by_ean/{game_ean}")
def return_game_ean(game_ean: str, db: Session = Depends(get_db), current_user: User = Depends(require_role("helper"))):
    game = db.query(Game).filter(Game.ean == game_ean).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"ean": game_ean})
    if game.available < game.quantity:
        game.available += 1
    else:
        game.available = game.quantity
    db.commit()
    db.refresh(game)
    return game