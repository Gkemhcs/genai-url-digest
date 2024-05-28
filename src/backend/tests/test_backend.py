import pytest
from app import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"everything is working fine" in response.data


def test_process_url(client):
    data = {
        "urls": ["https://example.com/page1", "https://example.com/page2"],
        "username": "test_user"
    }
    response = client.post('/process_url', data=data)
    assert response.status_code == 200
    assert b"ok" in response.data


def test_ask_question(client):
    data = {"question": "What is the capital of France?", "username": "test_user"}
    response = client.post('/ask_question', data=data)
    assert response.status_code == 200
    assert b"status" in response.data
    assert b"answer" in response.data

