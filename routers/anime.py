from fastapi import APIRouter, Depends, Query
from sqlmodel import Session, select
from models import Anime
from db import get_session

router = APIRouter(
    prefix = "/anime",
    tags = ["anime"]
)

@router.get("/", response_model = list[Anime])
def get_anime(
    q : str = Query(..., min_length = 1), 
    limit: int = Query(10, le=50),
    session: Session = Depends(get_session)
): 
    statement = select(Anime).where(Anime.title.contains(q)).limit(limit)
    results = session.exec(statement).all()
    return results 