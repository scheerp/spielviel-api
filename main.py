from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from database import engine, Base, SessionLocal
from models import Game, User
from fastapi.middleware.cors import CORSMiddleware
from auth import hash_password, create_access_token, verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from pydantic import BaseModel
from sqlalchemy import asc

Base.metadata.create_all(bind=engine)

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Abhängigkeit zur Datenbank-Sitzung
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    #allow_origins=["http://localhost:3000"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/register")
def register_user(username: str, password: str, db: Session = Depends(get_db)):
    hashed_pw = hash_password(password)
    user = User(username=username, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"message": "User created successfully", "username": user.username}

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falscher Benutzername oder Passwort",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

def get_admin_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(token, db)
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return user

@app.post("/create_game/")
def create_game(name: str,  ean: str, img_url: str = None, is_available: bool = True, bgg_id: int = None, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    game = Game(name=name, bgg_id=bgg_id, ean=ean, img_url=img_url, is_available=is_available)
    db.add(game)
    db.commit()
    db.refresh(game)
    return game

@app.get("/games")
def read_all_games(db: Session = Depends(get_db)):
    games = db.query(Game).order_by(asc(Game.name)).all()
    if not games:
        raise HTTPException(status_code=404, detail="Keine Spiele gefunden")
    return games

@app.get("/available_games")
def read_all_available_games(db: Session = Depends(get_db)):
    games = db.query(Game).filter(Game.is_available == True).all()
    if not games:
        raise HTTPException(status_code=404, detail="Keine verfügbaren Spiele gefunden")
    return games

@app.get("/game/{game_id}")
def read_game(game_id: int, db: Session = Depends(get_db)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")
    return game

class UpdateGameRequest(BaseModel):
    is_available: bool

@app.put("/update_game/{game_id}")
def update_game(game_id: int, request: UpdateGameRequest, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    game = db.query(Game).filter(Game.id == game_id).first()
    if game is None:
        raise HTTPException(status_code=404, detail="Spiel nicht gefunden")
    game.is_available = request.is_available
    db.commit()
    db.refresh(game)
    return game