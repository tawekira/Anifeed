from fastapi import FastAPI
from routers import anime, users, entries

app = FastAPI()

app.include_router(anime.router)
app.include_router(users.router)
app.include_router(entries.router)