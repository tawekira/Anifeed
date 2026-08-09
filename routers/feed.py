from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlmodel import Session, select
from sqlalchemy import or_, and_
from models import User, Follow, Event, CursorPaginatedResponse
from db import get_session
from security import get_current_user

router = APIRouter(
    prefix="/feed",
    tags=["feed"]
)

@router.get("/", response_model=CursorPaginatedResponse[Event])
def get_feed(
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session), 
    cursor: str | None = Query(None),
    limit: int = Query(20, ge=1, le=50)
):
    
    statement = select(Follow.followed_id).where(Follow.follower_id == user.id)
    followed = session.exec(statement).all()

    statement = select(Event).where(Event.user_id.in_(followed)).order_by(Event.created_at.desc(), Event.id.desc())
    if cursor: 
        try:
            cursor_created_at, id_str = cursor.rsplit("_", 1)
            cursor_id = int(id_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid cursor")
        statement = statement.where(or_(Event.created_at < cursor_created_at, and_(Event.created_at == cursor_created_at, Event.id < cursor_id)))

    events = session.exec(statement.limit(limit+1)).all()

    base_url = str(request.url).split('?')[0]
    next_url = None

    if len(events) > limit:
        last = events[:limit][-1]
        next_url = f"{base_url}?cursor={last.created_at}_{last.id}"

    response = CursorPaginatedResponse(
        data=events[:limit],
        next = next_url
    )

    return response



