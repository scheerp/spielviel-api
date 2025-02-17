import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
load_dotenv()

def get_database_url():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("❌ DATABASE_URL environment variable is not set")
    return database_url

# Engine erstellen
engine = create_engine(get_database_url())

# Session erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basis-Klasse für Modelle
Base = declarative_base()

# Abhängigkeit zur Datenbank-Sitzung
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
