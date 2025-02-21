from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routes.auth import router as auth_router
from routes.games import router as games_router
from routes.admin import router as admin_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://spiel-viel-tracker.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routen registrieren
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(games_router, prefix="/games", tags=["Games"])
app.include_router(admin_router, prefix="/admin", tags=["Admin"])

@app.get("/")
def read_root():
    return {"message": "Hello World"}


