from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import asc, desc, func
from database import get_db
from models import (
    Game,
    GameResponse,
    GamesWithCountResponse,
    GameResponseWithDetails,
    User,
    UserGameKnowledge,
    AddEANRequest,
    PlayerSearchResponse,
    Event,
    GameBorrow,
)
from utils.filters import apply_game_filters
from typing import List, Optional
from similar_games import get_top_similar_game_ids
from utils.errors import create_error
from auth import require_role
from datetime import datetime, timezone, timedelta


router = APIRouter()


def get_current_event(db: Session, year: Optional[int] = None) -> Event:
    """Gibt das Event des angegebenen Jahres zurück, default current year."""
    now = datetime.now(timezone.utc)
    target_year = year or now.year

    event = db.query(Event).filter(Event.year == target_year).first()
    if not event:
        raise ValueError(f"Kein Event für {target_year} gefunden in der DB!")

    return event


def is_event_active(event: Event) -> bool:
    """Prüft, ob das Event gerade stattfindet."""
    now = datetime.now(timezone.utc)

    # Falls das Event-naive Datetimes hat, als UTC interpretieren
    start = (
        event.start_date.replace(tzinfo=timezone.utc)
        if event.start_date.tzinfo is None
        else event.start_date
    )
    end = (
        event.end_date.replace(tzinfo=timezone.utc)
        if event.end_date.tzinfo is None
        else event.end_date
    )

    return start <= now <= end


@router.get("/", response_model=GamesWithCountResponse)
def read_all_games(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1),
    offset: int = Query(0, ge=0),
    filter_text: str = Query(None),
    show_available_only: bool = Query(False),
    min_player_count: int = Query(0, ge=0),
    player_age: int = Query(0, ge=0),
    show_missing_ean_only: bool = Query(False),
    complexities: list[str] = Query(
        None,
        description=(
            "Liste von Complexity-Labels "
            "(z.B. ?complexities=einsteiger&complexities=fortgeschritten)"
        ),
    ),
    user_id: int = Query(
        None, description="ID des Nutzers, für den my_familiarity geholt werden soll"
    ),
):
    query = db.query(Game).options(joinedload(Game.tags)).order_by(asc(Game.name))

    # 🔹 Automatische Barcode-Erkennung
    if filter_text and filter_text.isdigit() and 8 <= len(filter_text) <= 13:
        # Eindeutige EAN → Suche direkt
        query = query.filter(Game.ean == filter_text)
    else:
        # Normale Filterlogik
        query = apply_game_filters(
            query,
            filter_text,
            show_available_only,
            min_player_count,
            player_age,
            show_missing_ean_only,
            complexities,
        )

    total_games = query.count()
    games = query.offset(offset).limit(limit).all()

    user_familiarity = {}
    if user_id:
        user_knowledge = (
            db.query(UserGameKnowledge)
            .filter(UserGameKnowledge.user_id == user_id)
            .all()
        )
        user_familiarity = {uk.game_id: uk.familiarity for uk in user_knowledge}

    game_responses = [
        GameResponse(
            id=game.id,
            bgg_id=game.bgg_id,
            name=game.name,
            img_url=game.img_url,
            available=game.available,
            quantity=game.quantity,
            min_players=game.min_players or None,
            max_players=game.max_players or None,
            min_playtime=game.min_playtime or None,
            max_playtime=game.max_playtime or None,
            ean=game.ean or None,
            thumbnail_url=game.thumbnail_url or None,
            player_age=game.player_age or None,
            complexity=game.complexity or None,
            complexity_label=game.complexity_label or None,
            best_playercount=game.best_playercount or None,
            min_recommended_playercount=game.min_recommended_playercount or None,
            max_recommended_playercount=game.max_recommended_playercount or None,
            my_familiarity=user_familiarity.get(game.id),
            borrows_count=None,
        )
        for game in games
    ]

    return {"games": game_responses, "total": total_games}


@router.get("/count")
def get_games_count(
    db: Session = Depends(get_db),
    filter_text: str = Query(None, description="Filter nach Namen"),
    show_available_only: bool = Query(
        False, description="Nur verfügbare Spiele anzeigen"
    ),
    min_player_count: int = Query(0, ge=0, description="Minimale Spieleranzahl"),
    player_age: int = Query(0, ge=0, description="Minimales Alter der Spieler"),
    show_missing_ean_only: bool = Query(
        False, description="Nur Spiele ohne ean anzeigen"
    ),
    complexities: list[str] = Query(
        None,
        description=(
            "Liste von Complexity-Labels "
            "(z.B. ?complexities=einsteiger&complexities=fortgeschritten)"
        ),
    ),
):
    """
    Gibt die Gesamtanzahl der Spiele basierend auf den aktuellen Filtern zurück.
    """
    query = db.query(Game)
    query = apply_game_filters(
        query,
        filter_text,
        show_available_only,
        min_player_count,
        player_age,
        show_missing_ean_only,
        complexities,
    )
    total_count = query.count()

    return {"total_count": total_count}


@router.get("/game/{game_id}", response_model=GameResponseWithDetails)
def read_game(
    game_id: int,
    db: Session = Depends(get_db),
    edit_tokens: Optional[list[str]] = Query(None),
    expire_after_minutes: int = Query(15, ge=1),
):
    # Spiel abrufen, mit den zugehörigen Tags, ähnlichen Spielen und PlayerSearches
    game = (
        db.query(Game)
        .options(
            joinedload(Game.tags),
            joinedload(Game.similar_games),
            joinedload(Game.player_searches),  # PlayerSearches direkt laden
        )
        .filter(Game.id == game_id)
        .first()
    )

    if not game:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    # Heutiges Datum berechnen
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)
    valid_after = now - timedelta(minutes=expire_after_minutes)

    # PlayerSearches filtern (heute + noch gültig)
    filtered_player_searches = [
        search
        for search in game.player_searches
        if (search.game_id == game_id and today_start <= search.created_at < today_end)
    ]

    # Berechnen der `can_edit`-Flags für jedes gefilterte Gesuch
    if edit_tokens:
        for search in filtered_player_searches:
            search.can_edit = search.edit_token in edit_tokens
    else:
        for search in filtered_player_searches:
            search.can_edit = False

    # Rückgabe der Antwort, einschließlich aller erforderlichen Felder
    return GameResponseWithDetails(
        id=game.id,
        bgg_id=game.bgg_id,
        name=game.name,
        description=game.description or None,
        german_description=game.german_description or None,
        tags=game.tags,
        similar_games=top_similar_ids,
        player_searches=[
            PlayerSearchResponse(
                id=search.id,
                game_id=search.game_id,
                current_players=search.current_players,
                players_needed=search.players_needed,
                name=search.name,
                location=search.location,
                details=search.details or None,
                created_at=search.created_at,
                is_valid=search.created_at >= valid_after,
                can_edit=search.can_edit,
                edit_token=search.edit_token if search.can_edit else None,
            )
            for search in filtered_player_searches
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
        borrows_count=None,
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
    current_user: User = Depends(require_role("helper")),
    limit: int = Query(20, ge=1),
    year: Optional[int] = Query(None),
):
    event = get_current_event(db, year)

    # Query: Spieldaten + Summe der Borrows
    borrowed_query = (
        db.query(Game, func.sum(GameBorrow.count).label("total_borrows"))
        .join(GameBorrow, Game.id == GameBorrow.game_id)
        .filter(GameBorrow.event_id == event.id)
        .group_by(Game.id)
        .order_by(desc("total_borrows"))
        .limit(limit)
        .all()
    )

    # Gesamtanzahl aller Ausleihen
    total_borrows = (
        db.query(func.sum(GameBorrow.count))
        .filter(GameBorrow.event_id == event.id)
        .scalar()
    ) or 0

    # Mapping in GameResponse
    games = [
        GameResponse(
            id=game.Game.id,
            bgg_id=game.Game.bgg_id,
            name=game.Game.name,
            img_url=game.Game.img_url,
            available=game.Game.available,
            quantity=game.Game.quantity,
            min_players=game.Game.min_players,
            max_players=game.Game.max_players,
            min_playtime=game.Game.min_playtime,
            max_playtime=game.Game.max_playtime,
            ean=game.Game.ean,
            thumbnail_url=game.Game.thumbnail_url,
            player_age=game.Game.player_age,
            complexity=game.Game.complexity,
            complexity_label=game.Game.complexity_label,
            best_playercount=game.Game.best_playercount,
            min_recommended_playercount=game.Game.min_recommended_playercount,
            max_recommended_playercount=game.Game.max_recommended_playercount,
            my_familiarity=None,
            borrows_count=game.total_borrows,
        )
        for game in borrowed_query
    ]

    return GamesWithCountResponse(games=games, total=total_borrows)


@router.post("/by-ids", response_model=List[GameResponse])
def read_games_by_ids(game_ids: List[int], db: Session = Depends(get_db)):
    games = (
        db.query(Game)
        .options(joinedload(Game.tags))
        .filter(Game.id.in_(game_ids))
        .all()
    )
    if not games:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    # Mapping auf Pydantic-Model
    game_responses = [
        GameResponse(
            id=game.id,
            bgg_id=game.bgg_id,
            name=game.name,
            img_url=game.img_url,
            available=game.available,
            quantity=game.quantity,
            min_players=game.min_players or None,
            max_players=game.max_players or None,
            min_playtime=game.min_playtime or None,
            max_playtime=game.max_playtime or None,
            ean=game.ean or None,
            thumbnail_url=game.thumbnail_url or None,
            player_age=game.player_age or None,
            complexity=game.complexity or None,
            complexity_label=game.complexity_label or None,
            best_playercount=game.best_playercount or None,
            min_recommended_playercount=game.min_recommended_playercount or None,
            max_recommended_playercount=game.max_recommended_playercount or None,
            my_familiarity=None,
            borrows_count=None,
        )
        for game in games
    ]

    return game_responses


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
    current_user: User = Depends(require_role("helper")),
    force_event: bool = Query(
        False, description="Borrowings auch außerhalb des Events zählen"
    ),
):
    # 1. Datensatz mit Row-Level-Lock laden
    game = db.query(Game).filter(Game.id == game_id).with_for_update().first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    if game.available <= 0:
        create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")

    # 2. Verfügbarkeit verringern
    game.available -= 1

    # 3. Event-spezifisch Borrowings erhöhen
    event = get_current_event(db)
    borrow = db.query(GameBorrow).filter_by(game_id=game.id, event_id=event.id).first()

    if is_event_active(event) or force_event:
        if borrow:
            borrow.count += 1
        else:
            borrow = GameBorrow(game_id=game.id, event_id=event.id, count=1)
            db.add(borrow)

    # Falls kein Event aktiv und force_event=False, borrow bleibt ggf. None
    db.commit()
    db.refresh(game)
    if borrow:
        db.refresh(borrow)

    # 4. Beziehungen separat nachladen
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.id == game_id)
        .first()
    )

    # 5. Response zusammenbauen – sicher mit borrow_count
    borrow_count = borrow.count if borrow else 0

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": (
            [sg.similar_game_id for sg in game.similar_games]
            if game.similar_games
            else []
        ),
        "borrow_count": borrow_count,
    }


@router.put("/game/return/{game_id}")
def return_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper")),
):
    # Row-Level-Lock setzen ohne joinedload
    game = db.query(Game).filter(Game.id == game_id).with_for_update().first()
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

    # Borrow-count für Event abrufen (nicht ändern)
    event = get_current_event(db)
    borrow = db.query(GameBorrow).filter_by(game_id=game.id, event_id=event.id).first()

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": (
            [sg.similar_game_id for sg in game.similar_games]
            if game.similar_games
            else []
        ),
        "borrow_count": borrow.count if borrow else 0,
    }


@router.put("/game/add_ean/{game_id}")
def add_ean(
    game_id: int,
    request: AddEANRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper")),
):
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
                "thumbnail_url": existing_game.thumbnail_url,
            },
        )
    game.ean = request.ean
    db.commit()
    db.refresh(game)

    return game


@router.put("/game/remove_ean/{game_id}")
def remove_ean(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
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
    current_user: User = Depends(require_role("helper")),
    force_event: bool = Query(
        False, description="Borrowings auch außerhalb des Events zählen"
    ),
):
    # 1️⃣ Row-Level-Lock auf das Game via EAN
    game = db.query(Game).filter(Game.ean == game_ean).with_for_update().first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    if game.available <= 0:
        create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")

    # 2️⃣ Verfügbarkeit verringern
    game.available -= 1

    # 3️⃣ Borrowings für das Event des aktuellen Jahres
    event = get_current_event(db)
    borrow = db.query(GameBorrow).filter_by(game_id=game.id, event_id=event.id).first()

    if is_event_active(event) or force_event:
        if borrow:
            borrow.count += 1
        else:
            borrow = GameBorrow(game_id=game.id, event_id=event.id, count=1)
            db.add(borrow)

    # Event nicht aktiv → borrow_count fürs Event nicht ändern
    db.commit()
    db.refresh(game)
    if borrow:
        db.refresh(borrow)

    # 4️⃣ Beziehungen separat nachladen
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.ean == game_ean)
        .first()
    )

    # 5️⃣ Response sicher zusammenbauen
    borrow_count = borrow.count if borrow else 0

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": (
            [sg.similar_game_id for sg in game.similar_games]
            if game.similar_games
            else []
        ),
        "borrow_count": borrow_count,  # Event-spezifisch
    }


@router.put("/game/return_by_ean/{game_ean}")
def return_game_ean(
    game_ean: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper")),
):
    # 1️⃣ Row-Level-Lock auf das Game via EAN
    game = db.query(Game).filter(Game.ean == game_ean).with_for_update().first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    if game.available >= game.quantity:
        create_error(status_code=400, error_code="ALL_COPIES_AVAILABLE")

    # 2️⃣ Verfügbarkeit erhöhen
    game.available += 1
    db.commit()
    db.refresh(game)

    # 3️⃣ Borrowings für Event abrufen (nicht ändern)
    event = get_current_event(db)
    borrow = db.query(GameBorrow).filter_by(game_id=game.id, event_id=event.id).first()

    # 4️⃣ Beziehungen separat nachladen
    game = (
        db.query(Game)
        .options(selectinload(Game.similar_games), selectinload(Game.tags))
        .filter(Game.ean == game_ean)
        .first()
    )

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": (
            [sg.similar_game_id for sg in game.similar_games]
            if game.similar_games
            else []
        ),
        "borrow_count": borrow.count if borrow else 0,  # Event-spezifisch
    }


@router.put("/game/scan_by_ean/{game_ean}")
def scan_game_by_ean(
    game_ean: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("helper")),
    force_event: bool = Query(
        False, description="Borrowings auch außerhalb des Events zählen"
    ),
):
    # 1️⃣ Row-Level-Lock auf das Game via EAN
    game = db.query(Game).filter(Game.ean == game_ean).with_for_update().first()

    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND")

    event = get_current_event(db)

    borrow = db.query(GameBorrow).filter_by(game_id=game.id, event_id=event.id).first()

    action = "inconclusive"

    # ----------------------------
    # BORROW (alle verfügbar)
    # ----------------------------
    if game.available == game.quantity:

        if game.available <= 0:
            create_error(status_code=400, error_code="NO_COPIES_AVAILABLE")

        game.available -= 1

        if is_event_active(event) or force_event:
            if borrow:
                borrow.count += 1
            else:
                borrow = GameBorrow(
                    game_id=game.id,
                    event_id=event.id,
                    count=1,
                )
                db.add(borrow)

        action = "borrow"

    # ----------------------------
    # RETURN (keine verfügbar)
    # ----------------------------
    elif game.available == 0:

        if game.available >= game.quantity:
            create_error(status_code=400, error_code="ALL_COPIES_AVAILABLE")

        game.available += 1

        action = "return"

    # ----------------------------
    # COMMIT nur wenn Änderung
    # ----------------------------
    if action != "inconclusive":
        db.commit()
        db.refresh(game)

        if borrow:
            db.refresh(borrow)

    # ----------------------------
    # Beziehungen separat nachladen
    # ----------------------------
    game = (
        db.query(Game)
        .options(
            selectinload(Game.similar_games),
            selectinload(Game.tags),
        )
        .filter(Game.ean == game_ean)
        .first()
    )

    borrow_count = borrow.count if borrow else 0

    return {
        "action": action,
        **game.__dict__,
        "tags": game.tags,
        "similar_games": (
            [sg.similar_game_id for sg in game.similar_games]
            if game.similar_games
            else []
        ),
        "borrow_count": borrow_count,
    }
