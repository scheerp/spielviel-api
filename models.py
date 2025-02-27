from sqlalchemy import Table, Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from database import Base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict

game_tags = Table(
    "game_tags",
    Base.metadata,
    Column("game_id", Integer, ForeignKey("games.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class ExplainerResponse(BaseModel):
    id: int
    username: str
    familiarity: int

    class Config:
        from_attributes = True

class UserGameKnowledge(Base):
    __tablename__ = "user_game_knowledge"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    game_id = Column(Integer, ForeignKey("games.id"), primary_key=True)
    familiarity = Column(Integer, nullable=False)  # z.B. 0 = unbekannt, 5 = expertenwissen

    user = relationship("User", back_populates="game_knowledge")
    game = relationship("Game", back_populates="user_knowledge")

    
class ExplainersBasic(BaseModel):
    id: int
    username: str
    familiarity: int

    model_config = ConfigDict(from_attributes=True)

class UserGameKnowledgeRequest(BaseModel):
    game_id: int
    familiarity: int

class UserGameKnowledgeResponse(BaseModel):
    user_id: int
    game_id: int
    familiarity: int

    model_config = ConfigDict(from_attributes=True)

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    invite_code: str

class AddEANRequest(BaseModel):
    ean: str

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
    ean: Optional[str]
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
    complexity_label: Optional[str]
    best_playercount: Optional[int]
    min_recommended_playercount: Optional[int]
    max_recommended_playercount: Optional[int]
    explainers: Dict[int, List[ExplainersBasic]] = {} 
    my_familiarity: Optional[int] = None

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
    ean: Optional[str]
    available: int
    borrow_count: int
    quantity: int
    img_url: Optional[str]
    thumbnail_url: Optional[str]
    player_age: Optional[int]
    complexity: Optional[float]
    complexity_label: Optional[str]
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

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    bgg_id = Column(Integer, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    german_description = Column(String, nullable=True)
    year_published = Column(Integer, nullable=True)
    min_players = Column(Integer, nullable=True)
    max_players = Column(Integer, nullable=True)
    min_playtime = Column(Integer, nullable=True)
    max_playtime = Column(Integer, nullable=True)
    playing_time = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    ean = Column(String, unique=True, nullable=True)
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
    complexity_label = Column(String, nullable=True)
    best_playercount = Column(Integer, nullable=True)
    min_recommended_playercount = Column(Integer, nullable=True)
    max_recommended_playercount = Column(Integer, nullable=True)

    user_knowledge = relationship("UserGameKnowledge", back_populates="game")
    tags = relationship("Tag", secondary=game_tags, back_populates="games", cascade="all, delete")
    similar_games = relationship(
        "GameSimilarity",
        primaryjoin="Game.id == GameSimilarity.game_id",
        overlaps="game,similarities_from",
        cascade="all, delete-orphan"
    )

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="helper")
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)

    game_knowledge = relationship("UserGameKnowledge", back_populates="user")


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    normalized_tag = Column(String, unique=True, index=True, nullable=False)
    german_normalized_tag = Column(String, unique=True, index=True, nullable=False)
    synonyms = Column(String, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    games = relationship("Game", secondary=game_tags, back_populates="tags")
