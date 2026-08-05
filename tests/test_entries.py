from fastapi.testclient import TestClient
from main import app
from conftest import logged_in_context, seed_user1
from models import WatchStatus

client = TestClient(app)

def test_create_entry(logged_in_context, seed_user1):
    payload = {
        "anime_id": 1,
        "status": WatchStatus.COMPLETED,
        "episode": 1,
        "score": 8
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 200

    body = response.json()
    body.pop("updated_at")

    assert body == {
        "id": 1,
        "user_id": 1,
        "anime_id": 1,
        "status": WatchStatus.COMPLETED,
        "episode": 1,
        "score": 8
    }

# logic

def test_episodes_completed(logged_in_context, seed_user1):
    payload = {
        "anime_id": 3,
        "status": WatchStatus.WATCHING,
        "episode": 8,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 200

    body = response.json()
    body.pop("updated_at")

    assert body == {
        "id": 1,
        "user_id": 1,
        "anime_id": 3,
        "status": WatchStatus.COMPLETED,
        "episode": 8,
        "score": None
    }

def test_status_completed(logged_in_context, seed_user1):
    payload = {
        "anime_id": 3,
        "status": WatchStatus.COMPLETED,
        "episode": 5,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 200

    body = response.json()
    body.pop("updated_at")

    assert body == {
        "id": 1,
        "user_id": 1,
        "anime_id": 3,
        "status": WatchStatus.COMPLETED,
        "episode": 8,
        "score": None
    }

def test_status_watching_ongoing(logged_in_context, seed_user1):
    payload = {
        "anime_id": 58,
        "status": WatchStatus.WATCHING,
        "episode": 12,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 200

    body = response.json()
    body.pop("updated_at")

    assert body == {
        "id": 1,
        "user_id": 1,
        "anime_id": 58,
        "status": WatchStatus.WATCHING,
        "episode": 12,
        "score": None
    }

def test_status_plantowatch(logged_in_context, seed_user1):
    payload = {
        "anime_id": 1,
        "status": WatchStatus.PLANTOWATCH,
        "episode": 1,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 200

    body = response.json()
    body.pop("updated_at")

    assert body == {
        "id": 1,
        "user_id": 1,
        "anime_id": 1,
        "status": WatchStatus.PLANTOWATCH,
        "episode": 0,
        "score": None
    }

# Exceptions

def test_invalid_anime_id(logged_in_context, seed_user1):
    payload = {
        "anime_id": 0,
        "status": WatchStatus.COMPLETED,
        "episode": 5,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 404

def test_invalid_anime_episodes(logged_in_context, seed_user1):
    payload = {
        "anime_id": 1,
        "status": WatchStatus.COMPLETED,
        "episode": 10,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 400

def test_upcoming_anime_status(logged_in_context, seed_user1):
    payload = {
        "anime_id": 20,
        "status": WatchStatus.COMPLETED,
        "episode": 0,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 400

def test_upcoming_anime_episode(logged_in_context, seed_user1):
    payload = {
        "anime_id": 20,
        "status": WatchStatus.PLANTOWATCH,
        "episode": 1,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 400

def test_ongoing_anime_status(logged_in_context, seed_user1):
    payload = {
        "anime_id": 58,
        "status": WatchStatus.COMPLETED,
        "episode": 1,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user1"})
    assert response.status_code == 400



