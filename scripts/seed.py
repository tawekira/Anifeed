from sqlmodel import Session, select, func, SQLModel
import ijson
from models import Anime, User, WatchEntry, WatchStatus, Follow, Event, EventStatus, Notification, NotificationType
from security import get_password_hash
from datetime import datetime, timezone


def to_anime(entry: dict):
    score_data = entry.get("score")
    score = score_data.get("arithmeticGeometricMean") if score_data else None
    return Anime(
        title = entry["title"],
        type = entry["type"],
        episodes = entry["episodes"],
        status = entry["status"],
        season = entry["animeSeason"]["season"],
        year = entry["animeSeason"].get("year"),
        score = score,
        synonyms = entry["synonyms"],
        tags = entry["tags"],
        picture = entry["picture"],
        thumbnail = entry["thumbnail"]
    )

def stream_data():
    with open("data/anime-offline-database-minified.json", "rb") as f:
        for entry in ijson.items(f, "data.item"):
            yield entry

def batch_upload(engine, batch_size = 1000):
    with Session(engine) as session:
        batch = []
        count = 0
        for entry in stream_data():
            batch.append(to_anime(entry))
            if len(batch) >= batch_size:
                session.add_all(batch)
                session.commit()
                session.expunge_all()
                batch = []
                print(f"Inserted {count}")
        if batch:
            session.add_all(batch)
            session.commit()
            session.expunge_all()

def seed(engine):
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        existing = session.exec(select(func.count()).select_from(Anime)).one()
        if existing > 0:
            return 
        
        batch_upload(engine)

        jeremy = User(username="jeremy", hashed_password=get_password_hash("12345678"))
        jon = User(username="jonathan", hashed_password=get_password_hash("12345678"))
        session.add_all([jeremy, jon])
        session.commit()
        session.refresh(jeremy)
        session.refresh(jon)

        follow1 = Follow(follower_id=jeremy.id, followed_id=jon.id)
        follow2 = Follow(follower_id=jon.id, followed_id=jeremy.id)

        entry1 = WatchEntry(user_id=jeremy.id, anime_id=25735, status=WatchStatus.WATCHING, episode=1001, score=8, updated_at=datetime(2019, 3, 17, 8, 42, 51, tzinfo=timezone.utc))
        entry2 = WatchEntry(user_id=jeremy.id, anime_id=8847, status=WatchStatus.WATCHING, episode=28, score=7, updated_at=datetime(2019, 9, 4, 21, 15, 33, tzinfo=timezone.utc))
        entry3 = WatchEntry(user_id=jeremy.id, anime_id=15795, status=WatchStatus.COMPLETED, episode=24, score=9, updated_at=datetime(2020, 6, 22, 14, 7, 19, tzinfo=timezone.utc))
        entry4 = WatchEntry(user_id=jeremy.id, anime_id=388, status=WatchStatus.COMPLETED, episode=12, score=8, updated_at=datetime(2021, 11, 30, 2, 53, 46, tzinfo=timezone.utc))
        entry5 = WatchEntry(user_id=jeremy.id, anime_id=23941, status=WatchStatus.COMPLETED, episode=47, score=9, updated_at=datetime(2021, 11, 30, 2, 53, 46, tzinfo=timezone.utc))

        entry6 = WatchEntry(user_id=jon.id, anime_id=4813, status=WatchStatus.COMPLETED, episode=1, score=10, updated_at=datetime(2025, 12, 26, 21, 23, 22, tzinfo=timezone.utc))
        entry7 = WatchEntry(user_id=jon.id, anime_id=31688, status=WatchStatus.COMPLETED, episode=26, score=9, updated_at=datetime(2021, 1, 6, 6, 57, 52, tzinfo=timezone.utc))
        entry8 = WatchEntry(user_id=jon.id, anime_id=36224, status=WatchStatus.WATCHING, episode=7, score=9, updated_at=datetime(2020, 11, 8, 0, 26, 20, tzinfo=timezone.utc))
        entry9 = WatchEntry(user_id=jon.id, anime_id=15810, status=WatchStatus.WATCHING, episode=6, updated_at=datetime(2020, 12, 20, 14, 8, 15, tzinfo=timezone.utc))
        entry10 = WatchEntry(user_id=jon.id, anime_id=18546, status=WatchStatus.COMPLETED, episode=10, score=8, updated_at=datetime(2020, 1, 18, 11, 31, 0, tzinfo=timezone.utc))

        follows = [follow1, follow2]
        entries = [entry1, entry2, entry3, entry4, entry5, entry6, entry7, entry8, entry9, entry10]

        def get_events(entries, session):
            events = []
            for entry in entries:
                user = session.exec(select(User).where(User.id == entry.user_id)).first()
                anime = session.exec(select(Anime).where(Anime.id == entry.anime_id)).first()
                event_type = entry.status.to_event_status
                event = Event(
                    user_id=entry.user_id,
                    anime_id=entry.anime_id,
                    username=user.username,
                    anime_name=anime.title,
                    event_type=event_type,
                    event_metadata={"from_episode": 0, "to_episode": entry.episode},
                    created_at=entry.updated_at
                )
                events.append(event)
            return events

        events = get_events(entries, session)

        session.add_all(entries)
        session.add_all(events)
        session.add_all(follows)
        session.commit()
    
if __name__ == "__main__":
    from db import engine
    import models 
    seed(engine)





