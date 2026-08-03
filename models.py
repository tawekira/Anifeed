from sqlmodel import SQLModel, Field
from pydantic import BaseModel, Field as PydanticField
import sqlalchemy as sa
from sqlalchemy import Index, UniqueConstraint
from enum import StrEnum
from typing import Generic, TypeVar, Optional
from datetime import datetime, timezone

T = TypeVar("T")

class OffsetPaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    limit: int
    offset: int

class CursorPaginatedResponse(BaseModel, Generic[T]):
    data: list[Optional[T]]
    next: Optional[str]

class Type(StrEnum):
    TV = "TV"
    MOVIE = "MOVIE"
    OVA = "OVA"
    ONA = "ONA"
    SPECIAL = "SPECIAL"
    UNKNOWN = "UNKNOWN"

class AnimeStatus(StrEnum):
    FINISHED = "FINISHED"
    ONGOING = "ONGOING"
    UPCOMING = "UPCOMING"
    UNKNOWN = "UNKNOWN"

class Anime(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    type: Type
    episodes: int
    status: AnimeStatus
    synonyms: list[str] = Field(default=[], sa_type=sa.JSON)
    tags: list[str] = Field(default=[], sa_type=sa.JSON)
    picture: str
    thumbnail: str

class UserCreate(BaseModel):
    username: str = PydanticField(pattern=r"^[a-zA-Z0-9._]{3,20}$")

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(
        unique=True, 
        index=True, 
        regex=r"^[a-zA-Z0-9._]{3,20}$", 
        description="Username must be 3-20 characters and contain only alphanumeric, underscores, or periods."
    )

class WatchStatus(StrEnum):
    WATCHING = "Watching"
    COMPLETED = "Completed"
    ONHOLD = "On-Hold"
    DROPPED = "Dropped"
    PLANTOWATCH = "Plan to Watch"
    REWATCHING = "Rewatching"

    @property
    def to_event_status(self):
        mapping = {
            WatchStatus.WATCHING: EventStatus.WATCHED,
            WatchStatus.REWATCHING: EventStatus.REWATCHED,
            WatchStatus.COMPLETED: EventStatus.COMPLETED
        }
        return mapping.get(self)

class WatchEntryCreate(BaseModel):
    anime_id: int
    status: WatchStatus
    episode: int 
    score: int | None = Field(default=None, ge=1, le=10)
    
class WatchEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    anime_id: int = Field(foreign_key="anime.id", ondelete="CASCADE")
    status: WatchStatus
    episode: int | None = Field(default=None, ge=0)
    score: int | None = Field(default=None, ge=1, le=10)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
 
    __table_args__ = (
        Index("idx_watchentry_user_updated", "user_id", "updated_at"),
        UniqueConstraint("user_id", "anime_id", name="uq_watchentry_user_anime")
    )

class EventStatus(StrEnum):
    WATCHED = "Watched"
    REWATCHED = "Rewatched"
    COMPLETED = "Completed"
    RATED = "Rated"

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    anime_id: int = Field(foreign_key="anime.id", ondelete="CASCADE")
    username: str
    anime_name: str
    event_type: EventStatus
    event_metadata: dict = Field(sa_type=sa.JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_event_created_id", "created_at", "id"),
    )

class Follow(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    follower_id: int = Field(foreign_key="user.id", ondelete="CASCADE")
    followed_id: int = Field(foreign_key="user.id", ondelete="CASCADE")

    __table_args__ = (
        Index("idx_follow_follower", "follower_id"),
        UniqueConstraint("follower_id", "followed_id", name="uq_follow_pair")
    )


