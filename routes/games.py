from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import asc
from database import get_db
from models import Game, GameResponse, GamesWithCountResponse, GameResponseWithDetails, User, UserGameKnowledge, AddEANRequest, PlayerSearchResponse
from utils.filters import apply_game_filters
from typing import List, Optional
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
    complexities: list[str] = Query(None, description="Liste von Complexity-Labels (z.B. ?complexities=einsteiger&complexities=fortgeschritten)"),
    user_id: int = Query(None, description="ID des Nutzers, für den my_familiarity geholt werden soll")
):
    query = db.query(Game).options(joinedload(Game.tags)).order_by(asc(Game.name))
    query = apply_game_filters(query, filter_text, show_available_only, min_player_count, player_age, show_missing_ean_only, complexities)
    total_games = query.count()
    games = query.offset(offset).limit(limit).all()

    user_familiarity = {}
    if user_id:
        user_knowledge = db.query(UserGameKnowledge).filter(UserGameKnowledge.user_id == user_id).all()
        user_familiarity = {uk.game_id: uk.familiarity for uk in user_knowledge}

    game_responses = [
        GameResponse(
            **game.__dict__,
            my_familiarity=user_familiarity.get(game.id)
        )
        for game in games
    ]

    return {"games": game_responses, "total": total_games}


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
def read_game(game_id: int, db: Session = Depends(get_db), edit_tokens: Optional[list[str]] = Query(None)):
    game = db.query(Game).options(
        joinedload(Game.tags),
        joinedload(Game.similar_games),
        joinedload(Game.player_searches)  # PlayerSearches direkt laden
    ).filter(Game.id == game_id).first()

    if not game:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    # Berechnen der `can_edit`-Flags für jedes Gesuch
    if edit_tokens:
        for search in game.player_searches:
            search.can_edit = search.edit_token in edit_tokens
    else:
        for search in game.player_searches:
            search.can_edit = False

    # Rückgabe der Antwort, einschließlich aller erforderlichen Felder
    return GameResponseWithDetails(
        id=game.id,
        bgg_id=game.bgg_id,  # Sicherstellen, dass `bgg_id` gesetzt ist
        name=game.name,
        description=game.description or None,  # Fallback auf None, falls nicht vorhanden
        german_description=game.german_description or None,
        tags=game.tags,
        similar_games=[game_similar.id for game_similar in game.similar_games],
        player_searches=[
            PlayerSearchResponse(
                id=search.id,
                game_id=search.game_id,
                current_players=search.current_players,
                players_needed=search.players_needed,
                location=search.location,
                details=search.details or None,  # Falls keine Details vorhanden sind
                created_at=search.created_at,
                expires_at=search.expires_at,
                can_edit=search.can_edit,
                edit_token=search.edit_token if search.can_edit else None
            )
            for search in game.player_searches
        ],
        year_published=game.year_published or None,
        min_players=game.min_players or None,
        max_players=game.max_players or None,
        min_playtime=game.min_playtime or None,
        max_playtime=game.max_playtime or None,
        playing_time=game.playing_time or None,
        rating=game.rating or None,
        ean=game.ean or None,
        available=game.available,
        borrow_count=game.borrow_count,
        quantity=game.quantity,
        acquired_from=game.acquired_from or None,
        inventory_location=game.inventory_location or None,
        private_comment=game.private_comment or None,
        img_url=game.img_url or None,
        thumbnail_url=game.thumbnail_url or None,
        player_age=game.player_age or None,
        complexity=game.complexity or None,
        complexity_label=game.complexity_label or None,
        best_playercount=game.best_playercount or None,
        min_recommended_playercount=game.min_recommended_playercount or None,
        max_recommended_playercount=game.max_recommended_playercount or None,
    )



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