from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    bgg_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    ean = Column(String, unique=True, nullable=True)
    img_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")  # Beispielrollen: "user", "admin"