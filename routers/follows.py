from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError
from models import User, Follow, Notification, NotificationType
from db import get_session
from security import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["follows"]
)

@router.post("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def follow(
    username: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == username)
    followed = session.exec(statement).first()

    if not followed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Username not found")

    if followed.id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot follow yourself")

    statement = select(Follow).where(Follow.followed_id == followed.id, Follow.follower_id == user.id)
    existing = session.exec(statement).first()

    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Already following {username}")

    follow = Follow(follower_id=user.id, followed_id=followed.id)

    notification = Notification(
        user_id = followed.id,
        actor_username = user.username,
        notification_type = NotificationType.NEW_FOLLOWER
    )

    try:
        session.add(follow)
        session.add(notification)
        session.commit()

    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Already following {username}")

    return

@router.delete("/{username}/follow", status_code=status.HTTP_204_NO_CONTENT)
def unfollow(
    username: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(User).where(User.username == username)
    followed = session.exec(statement).first()

    if not followed:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Username not found")

    if followed.id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail = "Cannot unfollow yourself")

    statement = select(Follow).where(Follow.followed_id == followed.id, Follow.follower_id == user.id)
    existing = session.exec(statement).first()

    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = f"Not following {username}")

    session.delete(existing)
    session.commit()
    

