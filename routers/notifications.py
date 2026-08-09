from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models import Notification, NotificationType, User
from db import get_session
from security import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

@router.get("/", response_model=list[Notification])
def get_notifications(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = (
        select(Notification)
        .where(Notification.user_id == user.id, Notification.read == False)
        .order_by(Notification.created_at.desc())    
    )

    return session.exec(statement).all()

@router.post("/read-all", status_code=status.HTTP_204_NO_CONTENT)
def mark_all_read(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = (
        select(Notification)
        .where(Notification.user_id == user.id, Notification.read == False)  
    )

    unread = session.exec(statement).all()

    for notification in unread:
        notification.read = True
        session.add(notification)

    session.commit()


