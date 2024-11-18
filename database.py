from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Verbindung zur SQLite-Datenbank
SQLALCHEMY_DATABASE_URL = "sqlite:///./db.sqlite3"

# Engine erstellen
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Session erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis-Klasse für Modelle
Base = declarative_base()
