import pytest
from sqlmodel import SQLModel, Session, create_engine, text, select
from fastapi import Header, Depends, HTTPException, status
from main import app
from db import get_session, get_current_user
from models import User

TEST_DATABASE_URL = "sqlite:///./tests/test.db"

engine = create_engine(TEST_DATABASE_URL)

@pytest.fixture(autouse=True)
def db_transaction_and_overrides():
    connection = engine.connect()
    transaction = connection.begin()

    def get_session_override():
        with Session(bind=connection) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override

    yield 

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
        

