import pytest
from flask import g
from flask import session

from flaskr import db
from flaskr.auth.models import User


def test_register(client, app):
    # test that viewing the page renders without template errors
    assert client.get("/auth/register").status_code == 200

    # test that successful registration redirects to the login page
    response = client.post("/auth/register", data={"username": "a", "password": "a"})
    assert response.headers["Location"] == "/auth/login"

    # test that the user was inserted into the database
    with app.app_context():
        select = db.select(User).filter_by(username="a")
        user = db.session.execute(select).scalar()
        assert user is not None


def test_user_password(app):
    user = User(username="a", password="a")
    assert user.password_hash != "a"
    assert user.check_password("a")


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (
        ("", "", "Username is required."),
        ("a", "", "Password is required."),
        ("test", "test", "already registered"),
    ),
)
def test_register_validate_input(client, username, password, message):
    response = client.post(
        "/auth/register", data={"username": username, "password": password}
    )
    assert message in response.text


def test_login(client, auth):
    # test that viewing the page renders without template errors
    assert client.get("/auth/login").status_code == 200

    # test that successful login redirects to the index page
    response = auth.login()
    assert response.headers["Location"] == "/"

    # login request set the user_id in the session
    # check that the user is loaded from the session
    with client:
        client.get("/")
        assert session["user_id"] == 1
        assert g.user.username == "test"


@pytest.mark.parametrize(
    ("username", "password", "message"),
    (("a", "test", "Incorrect username."), ("test", "a", "Incorrect password.")),
)
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.text


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert "user_id" not in session
