from sqlalchemy import Column, Integer, String, Boolean, Float
from database import Base

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    bgg_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    year_published = Column(Integer, nullable=True )
    min_players = Column(Integer, nullable=True)
    max_players = Column(Integer, nullable=True)
    min_playtime = Column(Integer, nullable=True)
    max_playtime = Column(Integer, nullable=True)
    playing_time = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    ean = Column(String, unique=True, nullable=True)
    available = Column(Integer, default=1)
    borrow_count = Column(Integer, default=0)
    total_copies = Column(Integer, default=1)
    img_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")