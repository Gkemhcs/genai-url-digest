import pytest
from flask import Flask, session
from flask.testing import FlaskClient
import os
import redis  # Add this import
from app import app as flask_app

@pytest.fixture
def app() -> Flask:
    flask_app.config.update({
        "TESTING": True,
        "SECRET_KEY": "your_secret_key",
        "SESSION_TYPE": "redis",
        "SESSION_PERMANENT": False,
        "SESSION_USE_SIGNER": True,
        "SESSION_KEY_PREFIX": "session:",
        "SESSION_REDIS": redis.Redis(
            host=os.getenv("REDIS_SERVER_URL") or "localhost",
            port=6379,
            password=os.getenv("REDIS_AUTH_STRING") or "gkem1234",
            db=0, encoding='utf-8',
        ),
    })
    return flask_app

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

def login(client: FlaskClient, username: str):
    return client.post("/login", data={"username": username})

def test_home(client: FlaskClient):
    response = login(client, "testuser")
    assert response.status_code == 302  # Redirect after login

    response = client.get("/")
    assert response.status_code == 200
    assert b"LinkDigest" in response.data  # Check for the presence of the title in the HTML

def test_submit(client: FlaskClient, monkeypatch):
    response = login(client, "testuser")
    assert response.status_code == 302  # Redirect after login

    # Mock environment variables
    monkeypatch.setenv("BACKEND_SERVER_URL", "http://localhost:5001")

    response = client.post("/submit", data={"urls": ["https://example.com", "https://example.org"]})
    assert response.status_code == 200
    assert b"URLs submitted successfully" in response.data

def test_get_answer(client: FlaskClient, monkeypatch):
    response = login(client, "testuser")
    assert response.status_code == 302  # Redirect after login

    # Mock environment variables
    monkeypatch.setenv("BACKEND_SERVER_URL", "http://localhost:5001")

    response = client.post("/get_answer", data={"question": "What is Flask?"})
    assert response.status_code == 200
    assert b"LinkDigest" in response.data  # Check for the presence of the title in the HTML

def test_login_required(client: FlaskClient):
    response = client.get("/")
    assert response.status_code == 302  # Redirect to login

    response = client.get("/submit")
    assert response.status_code == 302  # Redirect to login

    response = client.get("/get_answer")
    assert response.status_code == 302  # Redirect to login
