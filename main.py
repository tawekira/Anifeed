from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import anime, users, entries, follows, feed, auth

app = FastAPI()

app.include_router(anime.router)
app.include_router(users.router)
app.include_router(entries.router)
app.include_router(follows.router)
app.include_router(feed.router)
app.include_router(auth.router)

origins = [
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)