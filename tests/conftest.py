from datetime import datetime

import flask
import pytest

from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    return app


@pytest.fixture
def db(app):
    return SQLAlchemy(app)


@pytest.fixture
def Todo(db):
    class Todo(db.Model):
        __tablename__ = "todos"
        id = db.Column("todo_id", db.Integer, primary_key=True)
        title = db.Column(db.String(60))
        text = db.Column(db.String)
        done = db.Column(db.Boolean)
        pub_date = db.Column(db.DateTime)

        def __init__(self, title, text):
            self.title = title
            self.text = text
            self.done = False
            self.pub_date = datetime.utcnow()

    db.create_all()
    yield Todo
    db.drop_all()
