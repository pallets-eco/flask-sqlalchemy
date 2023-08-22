from __future__ import annotations

import typing as t

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.session import Session


def test_scope(app: Flask, db: SQLAlchemy) -> None:
    with pytest.raises(RuntimeError):
        db.session()

    with app.app_context():
        first = db.session()
        second = db.session()
        assert first is second
        assert isinstance(first, Session)

    with app.app_context():
        third = db.session()
        assert first is not third


def test_custom_scope(app: Flask, model_class: t.Any) -> None:
    count = 0

    def scope() -> int:
        nonlocal count
        count += 1
        return count

    db = SQLAlchemy(app, model_class=model_class, session_options={"scopefunc": scope})

    with app.app_context():
        first = db.session()
        second = db.session()
        assert first is not second  # a new scope is generated on each call
        first.close()
        second.close()


@pytest.mark.usefixtures("app_ctx")
def test_session_class(app: Flask, model_class: t.Any) -> None:
    class CustomSession(Session):
        pass

    db = SQLAlchemy(
        app, model_class=model_class, session_options={"class_": CustomSession}
    )
    assert isinstance(db.session(), CustomSession)


@pytest.mark.usefixtures("app_ctx")
def test_session_uses_bind_key(app: Flask, model_class: t.Any) -> None:
    app.config["SQLALCHEMY_BINDS"] = {"a": "sqlite://"}
    db = SQLAlchemy(app, model_class=model_class)

    if issubclass(db.Model, (sa_orm.DeclarativeBase, sa_orm.DeclarativeBaseNoMeta)):

        class User(db.Model):
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, primary_key=True)

        class Post(db.Model):
            __bind_key__ = "a"
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, primary_key=True)

    else:

        class User(db.Model):  # type: ignore[no-redef]
            id = sa.Column(sa.Integer, primary_key=True)

        class Post(db.Model):  # type: ignore[no-redef]
            __bind_key__ = "a"
            id = sa.Column(sa.Integer, primary_key=True)

    assert db.session.get_bind(mapper=User) is db.engine
    assert db.session.get_bind(mapper=Post) is db.engines["a"]


@pytest.mark.usefixtures("app_ctx")
def test_get_bind_inheritance(app: Flask, model_class: t.Any) -> None:
    app.config["SQLALCHEMY_BINDS"] = {"a": "sqlite://"}
    db = SQLAlchemy(app, model_class=model_class)

    if issubclass(db.Model, (sa_orm.MappedAsDataclass)):

        class User(db.Model):
            __bind_key__ = "a"
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(
                sa.Integer, primary_key=True, init=False
            )
            type: sa_orm.Mapped[str] = sa_orm.mapped_column(
                sa.String, nullable=False, init=False
            )
            __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "user"}

        class Admin(User):
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(
                sa.ForeignKey(User.id), primary_key=True, init=False
            )
            org: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String, nullable=False)
            __mapper_args__ = {"polymorphic_identity": "admin"}

    elif issubclass(db.Model, (sa_orm.DeclarativeBase, sa_orm.DeclarativeBaseNoMeta)):

        class User(db.Model):  # type: ignore[no-redef]
            __bind_key__ = "a"
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(sa.Integer, primary_key=True)
            type: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String, nullable=False)
            __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "user"}

        class Admin(User):  # type: ignore[no-redef]
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(
                sa.ForeignKey(User.id), primary_key=True
            )
            org: sa_orm.Mapped[str] = sa_orm.mapped_column(sa.String, nullable=False)
            __mapper_args__ = {"polymorphic_identity": "admin"}

    else:

        class User(db.Model):  # type: ignore[no-redef]
            __bind_key__ = "a"
            id = sa.Column(sa.Integer, primary_key=True)
            type = sa.Column(sa.String, nullable=False)
            __mapper_args__ = {"polymorphic_on": type, "polymorphic_identity": "user"}

        class Admin(User):  # type: ignore[no-redef]
            id = sa.Column(sa.ForeignKey(User.id), primary_key=True)  # type: ignore[assignment]
            org = sa.Column(sa.String, nullable=False)
            __mapper_args__ = {"polymorphic_identity": "admin"}

    db.create_all()
    db.session.add(Admin(org="pallets"))
    db.session.commit()
    admin = db.session.execute(db.select(Admin)).scalar_one()
    db.session.expire(admin)
    assert admin.org == "pallets"
