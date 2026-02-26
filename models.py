from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    Float,
    ForeignKey,
    DateTime,
    func,
)
from database import Base
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class PlayerSearchCreate(BaseModel):
    name: str
    game_id: int
    current_players: int
    players_needed: int
    location: str
    details: Optional[str] = None


class PlayerSearchEdit(BaseModel):
    name: str
    current_players: int
    players_needed: int
    location: str
    details: Optional[str] = None
    edit_token: str


class PlayerSearchResponse(BaseModel):
    id: int
    game_id: int
    current_players: int
    players_needed: int
    location: str
    name: str
    details: Optional[str] = None
    can_edit: bool
    created_at: datetime
    is_valid: bool
    edit_token: Optional[str]
    game_name: Optional[str] = None
    max_players: Optional[int] = None
    img_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    best_playercount: Optional[int] = None


class PlayerSearchCreateResponse(BaseModel):
    id: int
    game_id: int
    name: str
    current_players: int
    players_needed: int
    location: str
    details: Optional[str] = None
    edit_token: str
    created_at: datetime


game_tags = Table(
    "game_tags",
    Base.metadata,
    Column(
        "game_id", Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True
    ),
    Column(
        "tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True
    ),
)


class UserGameKnowledge(Base):
    __tablename__ = "user_game_knowledge"

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), primary_key=True
    )
    familiarity = Column(Integer, nullable=False)

    user = relationship("User", back_populates="game_knowledge")
    game = relationship("Game", back_populates="user_knowledge")


class ExplainersBasic(BaseModel):
    id: int
    username: str
    familiarity: int

    model_config = ConfigDict(from_attributes=True)


class ExplainerGroup(BaseModel):
    familiarity: int
    users: List[ExplainersBasic]

    model_config = ConfigDict(from_attributes=True)


class GameExplainersResponse(BaseModel):
    my_familiarity: Optional[int]
    explainers: List[ExplainerGroup]

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
    player_searches: List[PlayerSearchResponse]

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
    my_familiarity: Optional[int] = None

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
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
    )
    similar_game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False, index=True
    )
    similarity_score = Column(Float, nullable=False)
    shared_tags_count = Column(Integer, nullable=False)
    tag_priority_sum = Column(Float, nullable=True)

    game = relationship("Game", foreign_keys=[game_id], backref="similarities_from")
    similar_game = relationship(
        "Game", foreign_keys=[similar_game_id], backref="similarities_to"
    )


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

    user_knowledge = relationship(
        "UserGameKnowledge", back_populates="game", cascade="all, delete-orphan"
    )
    tags = relationship(
        "Tag", secondary=game_tags, back_populates="games", cascade="all, delete"
    )
    player_searches = relationship(
        "PlayerSearch", back_populates="game", cascade="all, delete-orphan"
    )
    similar_games = relationship(
        "GameSimilarity",
        primaryjoin="Game.id == GameSimilarity.game_id",
        overlaps="game,similarities_from",
        cascade="all, delete-orphan",
    )


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    year = Column(Integer, nullable=False)


class GameBorrow(Base):
    __tablename__ = "game_borrows"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(
        Integer, ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    count = Column(Integer, default=0)

    event = relationship("Event", backref="borrows")
    game = relationship("Game", backref="borrows")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String, default="helper")
    reset_token = Column(String, nullable=True)
    reset_token_expires = Column(DateTime, nullable=True)
    force_password_change = Column(Boolean, default=False)

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


class PlayerSearch(Base):
    __tablename__ = "player_search"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    game_id = Column(
        Integer, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    current_players = Column(Integer, nullable=False)
    players_needed = Column(Integer, nullable=False)
    location = Column(String, nullable=False)
    details = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    edit_token = Column(String, unique=True, nullable=False)

    game = relationship("Game", back_populates="player_searches")


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
