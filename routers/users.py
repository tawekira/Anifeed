from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlmodel import Session, select
from models import User, UserCreate
from db import get_session, get_current_user

router = APIRouter(
    prefix = "/users",
    tags = ["users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(user_input: UserCreate, session: Session = Depends(get_session)):
    user = User.model_validate(user_input)

    statement = select(User).where(User.username == user_input.username)
    existing_username = session.exec(statement).first()

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = f"Username '{user_input.username}' is already taken"
        )

    session.add(user)
    session.commit()

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    session.delete(user)
    session.commit()


