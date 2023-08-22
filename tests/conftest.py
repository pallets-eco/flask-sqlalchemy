from __future__ import annotations

import types
import typing as t
from pathlib import Path

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import Flask
from flask.ctx import AppContext

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import Model


@pytest.fixture
def app(request: pytest.FixtureRequest, tmp_path: Path) -> Flask:
    app = Flask(request.module.__name__, instance_path=str(tmp_path / "instance"))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite://"
    app.config["SQLALCHEMY_RECORD_QUERIES"] = False
    return app


@pytest.fixture
def app_ctx(app: Flask) -> t.Generator[AppContext, None, None]:
    with app.app_context() as ctx:
        yield ctx


# Each test that uses the db or model_class fixture will be tested against
# each of these possible base class setups.
# The first one is None, which will trigger creation of a SQLAlchemy 1.x base.
# The remaining four are used to create SQLAlchemy 2.x bases.
# We defer creation of those classes until the fixture,
# so that each test gets a fresh class with its own metadata.
test_classes = [
    Model,
    (
        "BaseDeclarativeBase",
        (sa_orm.DeclarativeBase,),
        {"metaclass": type(sa_orm.DeclarativeBase)},
    ),
    (
        "BaseDataclassDeclarativeBase",
        (sa_orm.MappedAsDataclass, sa_orm.DeclarativeBase),
        {"metaclass": type(sa_orm.DeclarativeBase)},
    ),
    (
        "BaseDeclarativeBaseNoMeta",
        (sa_orm.DeclarativeBaseNoMeta,),
        {"metaclass": type(sa_orm.DeclarativeBaseNoMeta)},
    ),
    (
        "BaseDataclassDeclarativeBaseNoMeta",
        (
            sa_orm.MappedAsDataclass,
            sa_orm.DeclarativeBaseNoMeta,
        ),
        {"metaclass": type(sa_orm.DeclarativeBaseNoMeta)},
    ),
]


@pytest.fixture(params=test_classes)
def db(app: Flask, request: pytest.FixtureRequest) -> SQLAlchemy:
    if request.param is not Model:
        return SQLAlchemy(app, model_class=types.new_class(*request.param))
    else:
        return SQLAlchemy(app)


@pytest.fixture(params=test_classes)
def model_class(request: pytest.FixtureRequest) -> t.Any:
    if request.param is not Model:
        return types.new_class(*request.param)
    else:
        return request.param


@pytest.fixture
def Todo(app: Flask, db: SQLAlchemy) -> t.Generator[t.Any, None, None]:
    if issubclass(db.Model, (sa_orm.MappedAsDataclass)):

        class Todo(db.Model):
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(
                sa.Integer, init=False, primary_key=True
            )
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(
                sa.String, nullable=True, default=None
            )

    elif issubclass(db.Model, (sa_orm.DeclarativeBase, sa_orm.DeclarativeBaseNoMeta)):

        class Todo(db.Model):  # type: ignore[no-redef]
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, primary_key=True)
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String, nullable=True)

    else:

        class Todo(db.Model):  # type: ignore[no-redef]
            id = sa.Column(sa.Integer, primary_key=True)
            title = sa.Column(sa.String)

    with app.app_context():
        db.create_all()

    yield Todo

    with app.app_context():
        db.drop_all()
