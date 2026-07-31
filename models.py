from sqlmodel import SQLModel, Field
from pydantic import BaseModel, Field as PydanticField
import sqlalchemy as sa
from enum import StrEnum
from datetime import datetime, timezone

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

class WatchEntryCreate(BaseModel):
    anime_id: int
    status: WatchStatus
    episode: int 
    score: int | None = Field(default=None, ge=1, le=10)
    
class WatchEntry(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    anime_id: int = Field(foreign_key="anime.id")
    status: WatchStatus
    episode: int | None = Field(default=None, ge=0)
    score: int | None = Field(default=None, ge=1, le=10)

class EventStatus(StrEnum):
    WATCHED = "Watched"
    REWATCHED = "Rewatched"
    COMPLETED = "Completed"
    RATED = "Rated"

class Event(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    anime_id: int = Field(foreign_key="anime.id")
    event_type: EventStatus
    event_metadata: dict = Field(sa_type=sa.JSON)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))





