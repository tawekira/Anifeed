from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models import WatchEntry, WatchEntryCreate, Anime, User, WatchStatus, AnimeStatus
from db import get_session, get_current_user

router = APIRouter(
    prefix="/entries",
    tags = ["entries"]
)

@router.get("/{username}", response_model=list[WatchEntry])
def get_entry(username: str, session: Session = Depends(get_session)):
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Username not found")

    statement = select(WatchEntry).where(WatchEntry.user_id == user.id)
    entries = session.exec(statement).all()
    return entries

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

    final_status = user_entry.status
    final_episode = user_entry.episode

    if anime.status == AnimeStatus.UPCOMING and final_status in (WatchStatus.WATCHING, WatchStatus.REWATCHING, WatchStatus.COMPLETED):
        final_status = WatchStatus.PLANTOWATCH
        final_episode = 0
    elif anime.status == AnimeStatus.ONGOING and final_status == WatchStatus.COMPLETED:
        final_status = WatchStatus.WATCHING
    elif anime.episodes and user_entry.episode == anime.episodes and final_status in (WatchStatus.WATCHING, WatchStatus.REWATCHING):
        final_status = WatchStatus.COMPLETED

    if anime.episodes and final_status == WatchStatus.COMPLETED:
        final_episode = anime.episodes
            
    statement = select(WatchEntry).where(WatchEntry.anime_id == anime.id, WatchEntry.user_id == user.id)
    prev_entry = session.exec(statement).first()

    if prev_entry:
        if prev_entry.episode > user_entry.episode and final_status == WatchStatus.WATCHING:
            final_status = WatchStatus.REWATCHING
        prev_entry.status = final_status
        prev_entry.episode = final_episode
        prev_entry.score = user_entry.score
        session.add(prev_entry)
        session.commit()
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

        session.add(entry)
        session.commit()
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