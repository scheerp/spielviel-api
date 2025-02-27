from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import asc
from database import get_db
from models import Game, GameResponse, GamesWithCountResponse, GameResponseWithDetails, User, UserGameKnowledge, AddEANRequest, ExplainerResponse
from utils.filters import apply_game_filters
from typing import List, Optional
from similar_games import get_top_similar_game_ids
from utils.errors import create_error
from auth import require_role
from collections import defaultdict

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
def read_game(
    game_id: int,
    user_id: Optional[int] = Query(None, alias="user_id"),
    db: Session = Depends(get_db)
):
    game = (
        db.query(Game)
        .options(
            joinedload(Game.tags),
            joinedload(Game.similar_games),
            joinedload(Game.user_knowledge).joinedload(UserGameKnowledge.user)
        )
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    explainers_by_familiarity = defaultdict(list)
    for uk in game.user_knowledge:
        if uk.familiarity > 0:
            explainers_by_familiarity[uk.familiarity].append({
                "id": uk.user.id,
                "username": uk.user.username,
                "familiarity": uk.familiarity
            })

    explainers_by_familiarity = dict(sorted(explainers_by_familiarity.items(), reverse=True))

    my_familiarity = None
    if user_id is not None:
        for uk in game.user_knowledge:
            if uk.user.id == user_id:
                my_familiarity = uk.familiarity
                break

    response_data = {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": top_similar_ids,
        "my_familiarity": my_familiarity
    }

    if user_id is not None:
        response_data["explainers"] = explainers_by_familiarity

    return response_data



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
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")
    return games


@router.get("/game/by_ean/{ean}", response_model=GameResponse)
def read_game_by_ean(ean: str, db: Session = Depends(get_db)):
    game = db.query(Game).options(joinedload(Game.tags)).filter(Game.ean == ean).first()
    if not game:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")
    return game


@router.put("/game/borrow/{game_id}")
def borrow_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # 1. Datensatz mit Row-Level-Lock laden – ohne joinedload!
    game = (
        db.query(Game)
        .filter(Game.id == game_id)
        .with_for_update()
        .first()
    )
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")
    
    if game.available <= 0:
        create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")
    
    game.available -= 1
    game.borrow_count += 1
    db.commit()
    db.refresh(game)
    
    # 2. Nachladen der Beziehungen via selectinload (separate Abfrage)
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.id == game_id)
        .first()
    )
    
    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": [sg.similar_game_id for sg in game.similar_games] if game.similar_games else []
    }


@router.put("/game/return/{game_id}")
def return_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # Row-Level-Lock setzen ohne joinedload
    game = (
        db.query(Game)
        .filter(Game.id == game_id)
        .with_for_update()
        .first()
    )
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")
    
    if game.available >= game.quantity:
        create_error(status_code=400, error_code="ALL_COPIES_AVAILABLE")
    
    game.available += 1
    db.commit()
    db.refresh(game)
    
    # Beziehungen separat nachladen
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.id == game_id)
        .first()
    )
    
    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": [sg.similar_game_id for sg in game.similar_games] if game.similar_games else []
    }


@router.put("/game/add_ean/{game_id}")
def add_ean(game_id: int, request: AddEANRequest, db: Session = Depends(get_db), current_user: User = Depends(require_role("helper"))):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    existing_game = db.query(Game).filter(Game.ean == request.ean).first()
    if existing_game:
        create_error(
            status_code=409,
            error_code="BARCODE_CONFLICT",
            ean_details={
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
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    game.ean = None
    db.commit()
    db.refresh(game)

    return game

@router.put("/game/borrow_by_ean/{game_ean}")
def borrow_game_ean(
    game_ean: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # Row-Level-Lock setzen via EAN (ohne joinedload)
    game = (
        db.query(Game)
        .filter(Game.ean == game_ean)
        .with_for_update()
        .first()
    )
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")
    
    if game.available <= 0:
        create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")
    
    game.available -= 1
    game.borrow_count += 1
    db.commit()
    db.refresh(game)
    
    # Beziehungen separat nachladen
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.ean == game_ean)
        .first()
    )
    
    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": [sg.similar_game_id for sg in game.similar_games] if game.similar_games else []
    }


@router.put("/game/return_by_ean/{game_ean}")
def return_game_ean(
    game_ean: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(require_role("helper"))
):
    # Row-Level-Lock setzen via EAN (ohne joinedload)
    game = (
        db.query(Game)
        .filter(Game.ean == game_ean)
        .with_for_update()
        .first()
    )
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")
    
    if game.available >= game.quantity:
        create_error(status_code=400, error_code="ALL_COPIES_AVAILABLE")
    
    game.available += 1
    db.commit()
    db.refresh(game)
    
    # Beziehungen separat nachladen
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.ean == game_ean)
        .first()
    )
    
    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": [sg.similar_game_id for sg in game.similar_games] if game.similar_games else []
    }