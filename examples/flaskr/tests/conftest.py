from datetime import datetime

import pytest
from werkzeug.security import generate_password_hash

from flaskr import create_app
from flaskr import db
from flaskr import init_db
from flaskr.auth.models import User
from flaskr.blog.models import Post

_user1_pass = generate_password_hash("test")
_user2_pass = generate_password_hash("other")


@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # create the app with common test config
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})

    # create the database and load test data
    # set _password to pre-generated hashes, since hashing for each test is slow
    with app.app_context():
        init_db()
        user = User(username="test", password_hash=_user1_pass)
        db.session.add_all(
            (
                user,
                User(username="other", password_hash=_user2_pass),
                Post(
                    title="test title",
                    body="test\nbody",
                    author=user,
                    created=datetime(2018, 1, 1),
                ),
            )
        )
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """A test runner for the app's Click commands."""
    return app.test_cli_runner()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="test", password="test"):
        return self._client.post(
            "/auth/login", data={"username": username, "password": password}
        )

    def logout(self):
        return self._client.get("/auth/logout")


@pytest.fixture
def auth(client):
    return AuthActions(client)
