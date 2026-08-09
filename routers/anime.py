from fastapi import APIRouter, Depends, Query, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
import httpx
from models import Anime, AnimeStatus
from db import get_session

router = APIRouter(
    prefix = "/anime",
    tags = ["anime"]
)

@router.get("/proxy")
async def proxy_image(url: str):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, follow_redirects=True, timeout=10.0)
        except httpx.RequestError:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not fetch image")
        
    if response.status_code != 200:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Image source returned an error")

    content_type = response.headers.get("content-type", "image/jpeg")

    return StreamingResponse(
        iter([response.content]),
        media_type=content_type
    )

@router.get("/", response_model = list[Anime])
def get_anime(
    q : str | None = Query(None, min_length = 1), 
    status: AnimeStatus | None = Query(None),
    limit: int = Query(15, le=50),
    session: Session = Depends(get_session)
): 
    statement = select(Anime)

    if q:
        statement = statement.where(Anime.title.contains(q)).order_by(Anime.score.desc())
    if status:
        statement = statement.where(Anime.status == status).order_by(Anime.score.desc())

    statement = statement.limit(limit)
    results = session.exec(statement).all()
    return results 

@router.get("/{id}", response_model = Anime)
def get_anime(
    id: int,
    session: Session = Depends(get_session)
):
    anime = session.get(Anime, id)

    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")

    return anime