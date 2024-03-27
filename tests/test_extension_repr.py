from __future__ import annotations

import typing as t

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model


def test_repr_no_context() -> None:
    db: SQLAlchemy[t.Type[Model]] = SQLAlchemy()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    db.init_app(app)
    assert repr(db) == "<SQLAlchemy>"


def test_repr_default() -> None:
    db: SQLAlchemy[t.Type[Model]] = SQLAlchemy()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"

    db.init_app(app)
    with app.app_context():
        assert repr(db) == "<SQLAlchemy sqlite://>"


def test_repr_default_plustwo() -> None:
    db: SQLAlchemy[t.Type[Model]] = SQLAlchemy()
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_BINDS"] = {
        "a": "sqlite:///:memory:",
        "b": "sqlite:///test.db",
    }

    db.init_app(app)
    with app.app_context():
        assert repr(db) == "<SQLAlchemy sqlite:// +2 engines>"


def test_repr_nodefault() -> None:
    db: SQLAlchemy[t.Type[Model]] = SQLAlchemy()
    app = Flask(__name__)
    app.config["SQLALCHEMY_BINDS"] = {"x": "sqlite:///:memory:"}

    db.init_app(app)
    with app.app_context():
        assert repr(db) == "<SQLAlchemy (No default engine) +1 engines>"


def test_repr_nodefault_plustwo() -> None:
    db: SQLAlchemy[t.Type[Model]] = SQLAlchemy()
    app = Flask(__name__)
    app.config["SQLALCHEMY_BINDS"] = {
        "a": "sqlite:///:memory:",
        "b": "sqlite:///test.db",
    }

    db.init_app(app)
    with app.app_context():
        assert repr(db) == "<SQLAlchemy (No default engine) +2 engines>"
