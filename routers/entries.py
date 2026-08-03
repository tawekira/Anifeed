from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError
from models import WatchEntry, WatchEntryCreate, Anime, User, WatchStatus, AnimeStatus, Event, EventStatus, OffsetPaginatedResponse
from db import get_session, get_current_user
from datetime import datetime, timezone
from requests import Request

router = APIRouter(
    prefix="/entries",
    tags = ["entries"]
)

@router.get("/{username}", response_model=OffsetPaginatedResponse[WatchEntry])
def get_entry(
    username: str,
    session: Session = Depends(get_session), 
    page: int = Query(1, ge=1), 
    page_size: int = Query(20, ge=1, le=50)
):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Username not found")

    limit = page_size
    offset = (page-1) * limit

    base_query = select(WatchEntry).where(WatchEntry.user_id == user.id)

    total = session.exec(
        select(func.count()).select_from(base_query.subquery())
    ).one()

    entries = session.exec(
        base_query.order_by(WatchEntry.updated_at.desc()).offset(offset).limit(limit)
    ).all()

    response = OffsetPaginatedResponse(
        data = entries,
        total = total,
        limit = limit,
        offset = offset 
    )
    return response

@router.post("/", response_model=WatchEntry)
def create_entry(
    user_entry: WatchEntryCreate, 
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Anime).where(Anime.id == user_entry.anime_id)
    anime = session.exec(statement).first()

    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Anime not found")

    if anime.episodes and user_entry.episode > anime.episodes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = f"Episodes watched ({user_entry.episode}) cannot exceed anime total episode count ({anime.episodes})")

    if anime.status == AnimeStatus.UPCOMING and user_entry.status != WatchStatus.PLANTOWATCH:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Upcoming anime can only be added to your Plan to Watch list")

    if anime.status == AnimeStatus.UPCOMING and user_entry.episode != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Episodes watched for upcoming anime must be 0")

    if anime.status == AnimeStatus.ONGOING and user_entry.status == WatchStatus.COMPLETED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Ongoing anime cannot be marked as completed")
                            
    final_status = user_entry.status
    final_episode = user_entry.episode

    if anime.episodes and user_entry.episode == anime.episodes and (final_status in (WatchStatus.WATCHING, WatchStatus.REWATCHING) and anime.status != AnimeStatus.ONGOING):
        final_status = WatchStatus.COMPLETED

    if anime.episodes and final_status == WatchStatus.COMPLETED:
        final_episode = anime.episodes

    if final_status == WatchStatus.PLANTOWATCH:
        final_episode = 0
            
    statement = select(WatchEntry).where(WatchEntry.anime_id == anime.id, WatchEntry.user_id == user.id)
    prev_entry = session.exec(statement).first()

    # Event Logging
    event_type = final_status.to_event_status
    from_episode = prev_entry.episode if prev_entry else 0
    to_episode = final_episode

    if event_type:
        event = Event(
            user_id=user.id,
            anime_id=anime.id,
            username=user.username,
            anime_name=anime.title,
            event_type=event_type,
            event_metadata={"from_episode": from_episode, "to_episode": to_episode}
        )
        session.add(event)

    if user_entry.score:
        event = Event(
            user_id=user.id,
            anime_id=anime.id,
            username=user.username,
            anime_name=anime.title,
            event_type=EventStatus.RATED,
            event_metadata={"score": user_entry.score}
        )
        session.add(event)

    # Entry Logging
    if prev_entry:
        prev_entry.status = final_status
        prev_entry.episode = final_episode
        prev_entry.score = user_entry.score
        prev_entry.updated_at = datetime.now(timezone.utc)
        try:
            session.add(prev_entry)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="Entry already exists")
        session.refresh(prev_entry)
        return prev_entry

    else:
        entry = WatchEntry(
            user_id = user.id,
            anime_id = user_entry.anime_id,
            status = final_status,
            episode = final_episode,
            score = user_entry.score
        )

        try:
            session.add(entry)
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(status_code=409, detail="Entry already exists")
        session.refresh(entry)
        return entry

@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_entry(entry_id: int, user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    statement = select(WatchEntry).where(WatchEntry.id == entry_id, WatchEntry.user_id == user.id)
    entry = session.exec(statement).first()
    if entry:
        session.delete(entry)
        session.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail= "Entry not found"
        )