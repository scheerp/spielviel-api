from sqlalchemy import Table, Column, Integer, String, Boolean, Float, ForeignKey
from database import Base
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional

game_tags = Table(
    "game_tags",
    Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class AddEANRequest(BaseModel):
    ean: int

class TagResponse(BaseModel):
    id: int
    normalized_tag: str
    german_normalized_tag: str
    priority: int

    class Config:
        from_attributes = True

class SimilarGameResponse(BaseModel):
    similar_game_id: int
    similarity_score: float
    shared_tags_count: int
    tag_priority_sum: Optional[float]

    class Config:
        from_attributes = True

class GameResponseWithDetails(BaseModel):
    id: int
    bgg_id: int
    name: str
    description: Optional[str]
    german_description: Optional[str]
    tags: List[TagResponse]
    similar_games: List[int]
    year_published: Optional[int]
    min_players: Optional[int]
    max_players: Optional[int]
    min_playtime: Optional[int]
    max_playtime: Optional[int]
    playing_time: Optional[int]
    rating: Optional[float]
    ean: Optional[int]
    available: int
    borrow_count: int
    quantity: int
    acquired_from: Optional[str]
    inventory_location: Optional[str]
    private_comment: Optional[str]
    img_url: Optional[str]
    thumbnail_url: Optional[str]
    player_age: Optional[int]
    complexity: Optional[float]
    best_playercount: Optional[int]
    min_recommended_playercount: Optional[int]
    max_recommended_playercount: Optional[int]

    class Config:
        from_attributes = True

class GameResponse(BaseModel):
    id: int
    bgg_id: int
    name: str
    min_players: Optional[int]
    max_players: Optional[int]
    min_playtime: Optional[int]
    max_playtime: Optional[int]
    ean: Optional[int]
    available: int
    borrow_count: int
    quantity: int
    img_url: Optional[str]
    thumbnail_url: Optional[str]
    player_age: Optional[int]
    complexity: Optional[float]
    best_playercount: Optional[int]
    min_recommended_playercount: Optional[int]
    max_recommended_playercount: Optional[int]

    class Config:
        from_attributes = True

class GamesWithCountResponse(BaseModel):
    games: List[GameResponse]
    total: int

    class Config:
        from_attributes = True

class GameSimilarity(Base):
    __tablename__ = "game_similarities"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    similar_game_id = Column(Integer, ForeignKey("games.id"), nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)
    shared_tags_count = Column(Integer, nullable=False)
    tag_priority_sum = Column(Float, nullable=True)

    game = relationship("Game", foreign_keys=[game_id], backref="similarities_from")
    similar_game = relationship("Game", foreign_keys=[similar_game_id], backref="similarities_to")

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    bgg_id = Column(Integer, nullable=False, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    german_description = Column(String, nullable=True)
    tags = relationship("Tag", secondary=game_tags, back_populates="games", cascade="all, delete")
    similar_games = relationship(
        "GameSimilarity",
        primaryjoin="Game.id == GameSimilarity.game_id",
        overlaps="game,similarities_from",
        cascade="all, delete-orphan"
    )
    year_published = Column(Integer, nullable=True)
    min_players = Column(Integer, nullable=True)
    max_players = Column(Integer, nullable=True)
    min_playtime = Column(Integer, nullable=True)
    max_playtime = Column(Integer, nullable=True)
    playing_time = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    ean = Column(Integer, unique=True, nullable=True)
    available = Column(Integer, default=1)
    borrow_count = Column(Integer, default=0)
    quantity = Column(Integer, default=1)
    acquired_from = Column(String, nullable=True)
    inventory_location = Column(String, nullable=True)
    private_comment = Column(String, nullable=True)
    img_url = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    player_age = Column(Integer, nullable=True)
    complexity = Column(Float, nullable=True)
    best_playercount = Column(Integer, nullable=True)
    min_recommended_playercount = Column(Integer, nullable=True)
    max_recommended_playercount = Column(Integer, nullable=True)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="admin")

class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    normalized_tag = Column(String, unique=True, index=True, nullable=False)
    german_normalized_tag = Column(String, unique=True, index=True, nullable=False)
    synonyms = Column(String, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    games = relationship("Game", secondary=game_tags, back_populates="tags")