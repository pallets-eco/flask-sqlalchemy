from datetime import datetime

import flask
import os
import pytest

import flask_sqlalchemy as fsa


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    app._is_postgresql = 'postgresql' in os.environ.get('DB_ENGINE', '')
    if app._is_postgresql:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:@localhost:5432/travis_ci_test'
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    return app


@pytest.fixture
def db(app):
    return fsa.SQLAlchemy(app)


@pytest.fixture
def Todo(db):
    class Todo(db.Model):
        __tablename__ = 'todos'
        id = db.Column('todo_id', db.Integer, primary_key=True)
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
    db.session.rollback()
    db.drop_all()
