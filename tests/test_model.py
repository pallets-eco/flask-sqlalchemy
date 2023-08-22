from __future__ import annotations

import typing as t

import pytest
import sqlalchemy as sa
import sqlalchemy.exc as sa_exc
import sqlalchemy.orm as sa_orm
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.model import DefaultMeta
from flask_sqlalchemy.model import Model


def test_default_model_class_1x(app: Flask) -> None:
    db = SQLAlchemy(app)

    assert db.Model.query_class is db.Query
    assert db.Model.metadata is db.metadata
    assert issubclass(db.Model, Model)
    assert isinstance(db.Model, DefaultMeta)


def test_custom_model_class_1x(app: Flask) -> None:
    class CustomModel(Model):
        pass

    db = SQLAlchemy(app, model_class=CustomModel)
    assert issubclass(db.Model, CustomModel)
    assert isinstance(db.Model, DefaultMeta)


@pytest.mark.usefixtures("app_ctx")
@pytest.mark.parametrize("base", [Model, object])
def test_custom_declarative_class_1x(app: Flask, base: t.Any) -> None:
    class CustomMeta(DefaultMeta):
        pass

    CustomModel = sa_orm.declarative_base(cls=base, name="Model", metaclass=CustomMeta)
    db = SQLAlchemy(app, model_class=CustomModel)
    assert db.Model is CustomModel
    assert db.Model.query_class is db.Query
    assert "query" in db.Model.__dict__


def test_declarativebase_2x(app: Flask) -> None:
    class Base(sa_orm.DeclarativeBase):
        pass

    db = SQLAlchemy(app, model_class=Base)
    assert issubclass(db.Model, sa_orm.DeclarativeBase)
    assert isinstance(db.Model, sa_orm.decl_api.DeclarativeAttributeIntercept)


def test_declarativebasenometa_2x(app: Flask) -> None:
    class Base(sa_orm.DeclarativeBaseNoMeta):
        pass

    db = SQLAlchemy(app, model_class=Base)
    assert issubclass(db.Model, sa_orm.DeclarativeBaseNoMeta)
    assert not isinstance(db.Model, sa_orm.decl_api.DeclarativeAttributeIntercept)


def test_declarativebasemapped_2x(app: Flask) -> None:
    class Base(sa_orm.DeclarativeBase, sa_orm.MappedAsDataclass):
        pass

    db = SQLAlchemy(app, model_class=Base)
    assert issubclass(db.Model, sa_orm.DeclarativeBase)
    assert isinstance(db.Model, sa_orm.decl_api.DCTransformDeclarative)


def test_declarativebasenometamapped_2x(app: Flask) -> None:
    class Base(sa_orm.DeclarativeBaseNoMeta, sa_orm.MappedAsDataclass):
        pass

    db = SQLAlchemy(app, model_class=Base)
    assert issubclass(db.Model, sa_orm.DeclarativeBaseNoMeta)
    assert isinstance(db.Model, sa_orm.decl_api.DCTransformDeclarative)


@pytest.mark.usefixtures("app_ctx")
def test_model_repr(db: SQLAlchemy) -> None:
    class User(db.Model):
        id = sa.Column(sa.Integer, primary_key=True)

    db.create_all()
    user = User()

    if issubclass(db.Model, sa_orm.MappedAsDataclass):
        assert repr(user) == "test_model_repr.<locals>.User()"
    else:
        assert repr(user) == f"<User (transient {id(user)})>"
        db.session.add(user)
        assert repr(user) == f"<User (pending {id(user)})>"
        db.session.flush()
        assert repr(user) == f"<User {user.id}>"


@pytest.mark.usefixtures("app_ctx")
def test_too_many_bases(app: Flask) -> None:
    class Base(sa_orm.DeclarativeBase, sa_orm.DeclarativeBaseNoMeta):  # type: ignore[misc]
        pass

    with pytest.raises(ValueError):
        SQLAlchemy(app, model_class=Base)


@pytest.mark.usefixtures("app_ctx")
def test_disable_autonaming_true_sql1(app: Flask) -> None:
    db = SQLAlchemy(app, disable_autonaming=True)

    with pytest.raises(sa_exc.InvalidRequestError):

        class User(db.Model):
            id = sa.Column(sa.Integer, primary_key=True)


@pytest.mark.usefixtures("app_ctx")
def test_disable_autonaming_true_sql2(app: Flask) -> None:
    class Base(sa_orm.DeclarativeBase):
        pass

    db = SQLAlchemy(app, model_class=Base, disable_autonaming=True)

    with pytest.raises(sa_exc.InvalidRequestError):

        class User(db.Model):
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, primary_key=True)
