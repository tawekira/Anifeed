from fastapi.testclient import TestClient
from datetime import timedelta
from main import app
from conftest import seed_user1, seed_user2
from security import create_access_token

client = TestClient(app)

# Login

def test_login(seed_user1):
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "12345678"
        }
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"

def test_login_wrong_password(seed_user1):
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "wrong_password"
        }
    )
    assert response.status_code == 401

def test_login_nonexistent_username():
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "12345678"
        }
    )
    assert response.status_code == 401

# Token Validity

def test_valid_token(seed_user1, seed_user2):
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "12345678"
        }
    )
    token = response.json()["access_token"]

    response = client.post(
        "/users/user2/follow",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

def test_no_token(seed_user1, seed_user2):
    response = client.post(
        "/users/user2/follow"
    )
    assert response.status_code == 401

def test_tampered_token(seed_user1, seed_user2):
    token = create_access_token({"sub": "test"}, expires_delta=timedelta(minutes=60))
    token = token[:-5] + "aaaaa"
    response = client.post(
        "/users/user2/follow",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_expired_token(seed_user1, seed_user2):
    token = create_access_token({"sub": "user1"}, expires_delta=timedelta(seconds=-1))
    response = client.post(
        "/users/user2/follow",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401

def test_deleted_user(seed_user1, seed_user2):
    response = client.post(
        "/auth/token",
        data={
            "username": "user1",
            "password": "12345678"
        }
    )
    token = response.json()["access_token"]
    response = client.delete(
        "/users",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204
    response = client.post(
        "/users/user2/follow",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401




