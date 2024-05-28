import pytest
from flask import url_for
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config['TESTING'] = True
    flask_app.config['WTF_CSRF_ENABLED'] = False
    flask_app.config['SECRET_KEY'] = 'test_secret_key'
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()

def login(client, username):
    return client.post('/login', data=dict(username=username), follow_redirects=True)

def logout(client):
    return client.get('/logout', follow_redirects=True)

def test_home_page(client):
    """Test the home page access."""
    rv = client.get('/')
    assert rv.status_code == 302  # Redirects to login

    # Log in first
    login(client, 'testuser')
    rv = client.get('/')
    assert rv.status_code == 200
    assert b'LinkDigest' in rv.data

def test_login(client):
    """Test user login."""
    rv = client.post('/login', data=dict(username='testuser'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'LinkDigest' in rv.data

def test_login_no_username(client):
    """Test login without a username."""
    rv = client.post('/login', data=dict(username=''), follow_redirects=True)
    assert rv.status_code == 200
    assert b'Username is required!' in rv.data

def test_logout(client):
    """Test user logout."""
    login(client, 'testuser')
    rv = client.get('/logout', follow_redirects=True)
    assert rv.status_code == 200
    assert b'Login - LinkDigest' in rv.data

def test_submit_urls(client, monkeypatch):
    """Test URL submission."""
    login(client, 'testuser')

    def mock_post(url, data):
        class MockResponse:
            def __init__(self):
                self.status_code = 200
                self.text = '{"status": "ok"}'

            def json(self):
                return {"status": "ok"}
        
        return MockResponse()

    monkeypatch.setattr('requests.post', mock_post)

    rv = client.post('/submit', data=dict(urls=['http://example.com']), follow_redirects=True)
    assert rv.status_code == 200
    

def test_get_answer(client, monkeypatch):
    """Test asking a question."""
    login(client, 'testuser')

    def mock_post(url, data):
        class MockResponse:
            def __init__(self):
                self.status_code = 200

            def json(self):
                return {"answer": "This is a mock answer", "sources": ["Source 1", "Source 2"]}
        
        return MockResponse()

    monkeypatch.setattr('requests.post', mock_post)

    rv = client.post('/get_answer', data=dict(question='What is Flask?'), follow_redirects=True)
    assert rv.status_code == 200
    assert b'This is a mock answer' in rv.data
    assert b'Sources' in rv.data
    assert b'Source 1' in rv.data
    assert b'Source 2' in rv.data
