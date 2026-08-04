from fastapi import FastAPI
from routers import anime, users, entries, follows, feed, auth

app = FastAPI()

app.include_router(anime.router)
app.include_router(users.router)
app.include_router(entries.router)
app.include_router(follows.router)
app.include_router(feed.router)
app.include_router(auth.router)