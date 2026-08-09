from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select, func
from models import User, UserCreate, UserPublic, Follow, WatchEntry
from db import get_session
from security import get_current_user, get_password_hash, get_current_user_optional

router = APIRouter(
    prefix = "/users",
    tags = ["users"]
)

@router.get("/me", response_model=UserPublic)
def get_me(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    entries_count  = session.exec(
        select(func.count()).select_from(WatchEntry).where(WatchEntry.user_id == user.id)
    ).one()

    follower_count = session.exec(
        select(func.count()).select_from(Follow).where(Follow.followed_id == user.id)
    ).one()

    me = UserPublic(
        id = user.id,
        username = user.username,
        entries_count = entries_count,
        follower_count = follower_count
    )
    return me 

@router.get("/", response_model=list[UserPublic])
def get_user(
    q: str = Query(..., min_length=1),
    limit: int = Query(5, le=50), 
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user_optional)
):
    statement = select(User).where(User.username.contains(q))

    if current_user:
        statement = statement.where(User.id != current_user.id)

    statement = statement.limit(limit)
    users = session.exec(statement).all()

    results = []

    for user in users:
        entries_count  = session.exec(
            select(func.count()).select_from(WatchEntry).where(WatchEntry.user_id == user.id)
        ).one()

        follower_count = session.exec(
            select(func.count()).select_from(Follow).where(Follow.followed_id == user.id)
        ).one()

        is_following = False

        if current_user:
            following = session.exec(
                select(Follow).where(Follow.followed_id == user.id, Follow.follower_id == current_user.id)
            ).first()
            is_following = following is not None

        results.append(
            UserPublic(
                id = user.id,
                username = user.username,
                entries_count = entries_count,
                follower_count = follower_count,
                is_following = is_following
            )
        )

    return results

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user_input: UserCreate, session: Session = Depends(get_session)):

    statement = select(User).where(User.username == user_input.username)
    existing_username = session.exec(statement).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = f"Username '{user_input.username}' is already taken"
        )

    user = User(
        username=user_input.username,
        hashed_password=get_password_hash(user_input.password)
    )

    session.add(user)
    session.commit()

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    session.delete(user)
    session.commit()


