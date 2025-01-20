import os
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import engine, Base, SessionLocal
from models import Game, User, GameResponse, GameSimilarity, GameResponseWithSimilarGames, AddEANRequest
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import joinedload
from auth import hash_password, create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from sqlalchemy import asc
from typing import List
from fetch_and_store_private import fetch_and_store_private
from fetch_and_store_tags import save_tags_to_db
from similar_games import update_similar_games, get_top_similar_game_ids
from add_ean_bgg import add_ean_bgg
from database import Base, engine

# Fehlercodes zentral definieren
ERROR_CODES = {
    "GAME_NOT_FOUND": {"message": "Das Spiel wurde nicht gefunden."},
    "NO_GAMES_AVAILABLE": {"message": "Es sind keine Spiele verfügbar."},
    "BARCODE_CONFLICT": {"message": "Der EAN ist bereits einem anderen Spiel zugeordnet."},
    "NOT_AUTHORIZED": {"message": "Benutzer ist nicht autorisiert."},
    "PERMISSION_DENIED": {"message": "Keine Admin-Berechtigung."},
    "NO_COPIES_AVAILABLE": {"message": "Es sind keine verfügbaren Kopien vorhanden."},
    "ALL_COPIES_AVAILABLE": {"message": "Alle verfügbaren Kopien bereits zurückgegeben."},
    "USER_ALREADY_EXISTS": {"message": "Der Benutzername ist bereits vergeben."},
}

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Helper-Funktion für Fehler
def create_error(status_code: int, error_code: str, details: dict = None):
    error = ERROR_CODES.get(error_code, {"message": "Unbekannter Fehler"})
    raise HTTPException(
        status_code=status_code,
        detail={
            "error_code": error_code,
            "message": error["message"],
            "details": details or {}
        }
    )


# Abhängigkeit zur Datenbank-Sitzung
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://spiel-viel-tracker.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bgg_username = os.getenv("BGG_USERNAME")
bgg_password = os.getenv("BGG_PASSWORD")
#fetch_and_store_private(bgg_username, bgg_password)

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        create_error(status_code=status.HTTP_401_UNAUTHORIZED, error_code="NOT_AUTHORIZED")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        create_error(status_code=status.HTTP_409_CONFLICT, error_code="USER_ALREADY_EXISTS")
    hashed_pw = hash_password(password)
    user = User(username=username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "username": user.username}


def get_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "admin":
        create_error(status_code=status.HTTP_403_FORBIDDEN, error_code="PERMISSION_DENIED")
    return user


@app.post("/create_game/")
def create_game(name: str, ean: str, img_url: str = None, is_available: bool = True, bgg_id: int = None,
                db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    game = Game(name=name, bgg_id=bgg_id, ean=ean, img_url=img_url, is_available=is_available)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


@app.get("/games", response_model=List[GameResponse])
def read_all_games(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, description="Anzahl der Spiele pro Seite"),
    offset: int = Query(0, ge=0, description="Startindex für die Spiele"),
    filter_text: str = Query(None, description="Filter nach Namen"),
    show_available_only: bool = Query(False, description="Nur verfügbare Spiele anzeigen"),
    min_player_count: int = Query(1, ge=1, description="Minimale Spieleranzahl")
):
    query = db.query(Game).options(joinedload(Game.tags)).order_by(asc(Game.name))
    
    # Filter nach Namen
    if filter_text:
        query = query.filter(Game.name.ilike(f"%{filter_text}%"))

    # Nur verfügbare Spiele
    if show_available_only:
        query = query.filter(Game.available > 0)

    # Filter nach Spieleranzahl
    query = query.filter(Game.max_players >= min_player_count)

    # Pagination
    games = query.offset(offset).limit(limit).all()

    if not games:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")

    return games

@app.get("/available_games", response_model=List[GameResponse])
def read_all_available_games(db: Session = Depends(get_db)):
    games = db.query(Game).options(joinedload(Game.tags)).filter(Game.available > 0).all()
    if not games:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE")
    return games

@app.get("/game/{game_id}", response_model=GameResponseWithSimilarGames)
def read_game(game_id: int, db: Session = Depends(get_db)):
    game = (
        db.query(Game)
        .options(joinedload(Game.tags), joinedload(Game.similar_games))
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found.")

    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": top_similar_ids  # Nur IDs der 5 ähnlichsten Spiele
    }

@app.post("/games/by-ids", response_model=List[GameResponse])
def read_games_by_ids(game_ids: List[int], db: Session = Depends(get_db)):
    games = db.query(Game).options(joinedload(Game.tags)).filter(Game.id.in_(game_ids)).all()
    if not games:
        create_error(status_code=404, error_code="NO_GAMES_AVAILABLE", details={"game_ids": game_ids})
    return games

@app.get("/game_by_ean/{ean}", response_model=GameResponse)
def read_game_by_ean(ean: int, db: Session = Depends(get_db)):
    game = db.query(Game).options(joinedload(Game.tags)).filter(Game.ean == ean).first()
    if not game:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"ean": ean})
    return game

@app.get("/game/{game_id}", response_model=GameResponseWithSimilarGames)
def read_game(game_id: int, db: Session = Depends(get_db)):
    game = (
        db.query(Game)
        .options(joinedload(Game.tags), joinedload(Game.similar_games))
        .filter(Game.id == game_id)
        .first()
    )
    if not game:
        raise HTTPException(status_code=404, detail=f"Game with ID {game_id} not found.")

    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": top_similar_ids
    }

@app.put("/borrow_game/{game_id}")
def borrow_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
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
    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    # Rückgabe des aktualisierten Spiels mit ähnlichen Spielen
    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": top_similar_ids  # IDs der 5 ähnlichsten Spiele
    }


@app.put("/return_game/{game_id}")
def return_game(
    game_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_admin_user)
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
    top_similar_ids = get_top_similar_game_ids(game.similar_games)

    # Rückgabe des aktualisierten Spiels mit ähnlichen Spielen
    return {
        **game.__dict__,
        "tags": game.tags,
        "similar_games": top_similar_ids  # IDs der 5 ähnlichsten Spiele
    }


@app.put("/add_ean/{game_id}")
def add_ean(game_id: int, request: AddEANRequest, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
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

    #try:
    #    updated_textarea_content = add_ean_bgg(bgg_username, bgg_password, game.bgg_id, request.ean)
    #except Exception as e:
    #    raise HTTPException(status_code=500, detail=str(e))

    #game.private_comment = updated_textarea_content
    game.ean = request.ean
    db.commit()
    db.refresh(game)

    return game


@app.put("/borrow_game_ean/{game_ean}")
def borrow_game_ean(game_ean: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
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


@app.put("/return_game_ean/{game_ean}")
def return_game_ean(game_ean: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    game = db.query(Game).filter(Game.ean == game_ean).first()
    if game is None:
        create_error(status_code=404, error_code="GAME_NOT_FOUND", details={"ean": game_ean})
    if game.available < game.total_copies:
        game.available += 1
    else:
        game.available = game.total_copies
    db.commit()
    db.refresh(game)
    return game


@app.post("/fetch_private_collection")
def fetch_private_collection(db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    try:
        collection = fetch_and_store_private(bgg_username, bgg_password)
        return collection
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fetch_tags")
def fetch_tags_endpoint(db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    """
    Endpoint to fetch tags from external sources and save them in the database.
    """
    try:
        save_tags_to_db()
        return {"message": "Tags fetched and saved successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating tags: {str(e)}")


@app.post("/update_similar_games")
def update_similar_games_endpoint(db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    """
    Endpoint to find and update similar games based on their tags.
    """
    try:
        update_similar_games()
        return {"message": "Similar games updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating similar games: {str(e)}")
