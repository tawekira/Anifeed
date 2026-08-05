from fastapi.testclient import TestClient
from main import app
from conftest import logged_in_context

client = TestClient(app)

def test_create_user():
    payload = {"username": "test_user", "password": "12345678"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201

def test_duplicate_user():
    payload = {"username": "test_user", "password": "12345678"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201

    payload = {"username": "test_user", "password": "12345678"}
    response = client.post("/users", json=payload)
    assert response.status_code == 400

def test_invalid_user():
    payload = {"username": "bad@user!", "password": "12345678"}
    response = client.post(
        "/users",
        json=payload
    )
    assert response.status_code == 422

def test_delete_user(logged_in_context):
    payload = {"username": "test_user", "password": "12345678"}
    response = client.post("/users", json=payload)
    assert response.status_code == 201

    username = "test_user"
    response = client.delete(
        "/users",
        headers={"user": username}
    )
    assert response.status_code == 204

def test_delete_nonexistent_user():
    username = "test_user"
    response = client.delete(
        "/users",
        headers={"user": username}

    )
    assert response.status_code == 401
    

