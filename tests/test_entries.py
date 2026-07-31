from fastapi.testclient import TestClient
from main import app
from conftest import logged_in_context
from models import WatchStatus

client = TestClient(app)

def test_create_entry(logged_in_context):
    payload = {
        "anime_id": 1,
        "status": WatchStatus.COMPLETED,
        "episode": 1,
        "score": 8
    }
    response = client.post("/entries", json=payload, headers={"user": "user"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "anime_id": 1,
        "status": WatchStatus.COMPLETED,
        "episode": 1,
        "score": 8
    }

def test_plan_to_watch(logged_in_context):
    payload = {
        "anime_id": 20,
        "status": WatchStatus.COMPLETED,
        "episode": 1,
        "score": None
    }
    response = client.post("/entries", json=payload, headers={"user": "user"})
    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "user_id": 1,
        "anime_id": 20,
        "status": WatchStatus.PLANTOWATCH,
        "episode": 0,
        "score": None
    }


