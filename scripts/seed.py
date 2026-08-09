from sqlmodel import Session
import json
from models import Anime, User
from security import create_access_token

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

def load_data():
    with open("data/anime-offline-database-minified.json", "r", encoding = "utf-8") as f:
        payload = json.load(f)
    return payload["data"]

def batch_upload(data, engine, batch_size = 1000):
    with Session(engine) as session:
        batch = []
        for i, entry in enumerate(data, start=1):
            batch.append(to_anime(entry))
            if len(batch) >= batch_size:
                session.add_all(batch)
                session.commit()
                batch = []
                print(f"Inserted {i}/{len(data)}")
        if batch:
            session.add_all(batch)
            session.commit()

if __name__ == "__main__":
    from db import engine
    import models
    from sqlmodel import SQLModel

    SQLModel.metadata.create_all(engine)
    data = load_data()
    batch_upload(data, engine)






