from __future__ import annotations

import types
import typing as t

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import Flask
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import DeclarativeBaseNoMeta
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import MappedAsDataclass

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.model import Model


def test_default_model_class(db: SQLAlchemy) -> None:
    assert db.Model.query_class is db.Query
    assert db.Model.metadata is db.metadata
    assert issubclass(db.Model, Model)
    assert isinstance(db.Model, DefaultMeta)


def test_custom_model_class(app: Flask) -> None:
    class CustomModel(Model):
        pass

    db = SQLAlchemy(app, model_class=CustomModel)
    assert issubclass(db.Model, CustomModel)
    assert isinstance(db.Model, DefaultMeta)


test_classes = [
    types.new_class(
        "BaseModel", (DeclarativeBase,), {"metaclass": type(sa.orm.DeclarativeBase)}
    ),
    types.new_class(
        "BaseMappedModel",
        (MappedAsDataclass, DeclarativeBase),
        {"metaclass": type(sa.orm.DeclarativeBase)},
    ),
    types.new_class(
        "BaseModel",
        (DeclarativeBaseNoMeta,),
        {"metaclass": type(sa.orm.DeclarativeBaseNoMeta)},
    ),
    types.new_class(
        "BaseModel",
        (
            MappedAsDataclass,
            DeclarativeBaseNoMeta,
        ),
        {"metaclass": type(sa.orm.DeclarativeBaseNoMeta)},
    ),
]


@pytest.mark.usefixtures("app_ctx")
@pytest.mark.parametrize("base", test_classes)
def test_sqlalchemy20(app: Flask, base: object) -> None:
    from sqlalchemy.orm.decl_api import DeclarativeAttributeIntercept

    app.config["SQLALCHEMY_BINDS"] = {"other": "sqlite://"}
    db = SQLAlchemy(app, model_class=base)

    # Check the model class is instantiated with the correct metaclass
    if issubclass(db.Model, DeclarativeBase) or issubclass(db.Model, MappedAsDataclass):
        assert isinstance(db.Model, DeclarativeAttributeIntercept)
    elif issubclass(db.Model, DeclarativeBaseNoMeta) and not issubclass(
        db.Model, MappedAsDataclass
    ):
        assert not isinstance(db.Model, DeclarativeAttributeIntercept)
    # Check that additional attributes are added to the model class
    assert db.Model.query_class is db.Query
    assert db.Model.__fsa__ is db

    if issubclass(base, MappedAsDataclass):
        id_column = mapped_column(init=False, primary_key=True, autoincrement=True)
    else:
        id_column = mapped_column(primary_key=True, autoincrement=True)

    # Now create a model that inherits from that declarative base
    class Quiz(db.Model):
        __bind_key__ = "other"
        id: Mapped[int] = id_column
        title: Mapped[str] = mapped_column(db.String(255), nullable=False)

    assert Quiz.__tablename__ == "quiz"
    assert Quiz.metadata is db.metadatas["other"]

    db.create_all()
    quiz = Quiz(title="Python trivia")
    db.session.add(quiz)
    db.session.commit()

    # Check column types are correct
    quiz_id: int = quiz.id
    quiz_title: str = quiz.title
    assert quiz_id == 1
    assert quiz_title == "Python trivia"
    if issubclass(base, MappedAsDataclass):
        assert (
            repr(quiz) == "test_sqlalchemy20.<locals>.Quiz(id=1, title='Python trivia')"
        )
    else:
        assert repr(quiz) == f"<Quiz {quiz.id}>"


@pytest.mark.usefixtures("app_ctx")
@pytest.mark.parametrize("base", [Model, object])
def test_custom_declarative_class(app: Flask, base: t.Any) -> None:
    class CustomMeta(DefaultMeta):
        pass

    CustomModel = sa_orm.declarative_base(cls=base, name="Model", metaclass=CustomMeta)
    db = SQLAlchemy(app, model_class=CustomModel)
    assert db.Model is CustomModel
    assert db.Model.query_class is db.Query
    assert "query" in db.Model.__dict__


@pytest.mark.usefixtures("app_ctx")
def test_model_repr(db: SQLAlchemy) -> None:
    class User(db.Model):
        id = sa.Column(sa.Integer, primary_key=True)

    db.create_all()
    user = User()
    assert repr(user) == f"<User (transient {id(user)})>"
    db.session.add(user)
    assert repr(user) == f"<User (pending {id(user)})>"
    db.session.flush()
    assert repr(user) == f"<User {user.id}>"
