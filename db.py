from sqlmodel import SQLModel, create_engine, Session, select
from fastapi import Header, Depends, HTTPException, status
from models import Anime, User

sqlite_file_name = "app.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo = True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def get_current_user(
    user: str = Header(...),
    session: Session = Depends(get_session)
): 
    user = session.exec(select(User).where(User.username == user)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user
        
if __name__ == "__main__":
    create_db_and_tables()