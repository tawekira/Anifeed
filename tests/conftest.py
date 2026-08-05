import pytest
from sqlmodel import SQLModel, Session, create_engine, text, select
from fastapi import Header, Depends, HTTPException, status
from main import app
from db import get_session
from models import User
from security import get_password_hash, get_current_user

TEST_DATABASE_URL = "sqlite:///./tests/test.db"

engine = create_engine(TEST_DATABASE_URL)

@pytest.fixture(autouse=True, name="session")
def db_transaction_and_overrides():
    connection = engine.connect()
    transaction = connection.begin()

    with Session(bind=connection) as session:
        def get_session_override():
            yield session

        app.dependency_overrides[get_session] = get_session_override

        yield session

    transaction.rollback()
    connection.close()
    app.dependency_overrides.clear()

@pytest.fixture()
def logged_in_context():
    def get_current_user_override(
            user: str = Header(...),
            session: Session = Depends(get_session)
    ):
        user = session.exec(select(User).where(User.username == user)).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return user

    app.dependency_overrides[get_current_user] = get_current_user_override
    yield
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]

@pytest.fixture()
def seed_user1(
    session: Session
):
    user1 = User(username="user1", hashed_password=get_password_hash("12345678"))
    session.add(user1)
    session.commit()
    session.refresh(user1)

@pytest.fixture()
def seed_user2(
    session: Session
):
    user2 = User(username="user2", hashed_password=get_password_hash("12345678"))
    session.add(user2)
    session.commit()
    session.refresh(user2)


