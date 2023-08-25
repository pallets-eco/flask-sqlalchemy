from __future__ import annotations

import typing as t
from datetime import datetime

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
def test_declaredattr(app: Flask, model_class: t.Any) -> None:
    if model_class is Model:

        class IdModel(Model):
            @sa.orm.declared_attr
            @classmethod
            def id(cls: type[Model]):  # type: ignore[no-untyped-def]
                for base in cls.__mro__[1:-1]:
                    if getattr(base, "__table__", None) is not None and hasattr(
                        base, "id"
                    ):
                        return sa.Column(sa.ForeignKey(base.id), primary_key=True)
                return sa.Column(sa.Integer, primary_key=True)

        db = SQLAlchemy(app, model_class=IdModel)

        class User(db.Model):
            name = db.Column(db.String)

        class Employee(User):
            title = db.Column(db.String)

    else:

        class Base(sa_orm.DeclarativeBase):
            @sa_orm.declared_attr
            @classmethod
            def id(cls: type[sa_orm.DeclarativeBase]) -> sa_orm.Mapped[int]:
                for base in cls.__mro__[1:-1]:
                    if getattr(base, "__table__", None) is not None and hasattr(
                        base, "id"
                    ):
                        return sa_orm.mapped_column(
                            db.ForeignKey(base.id), primary_key=True
                        )
                return sa_orm.mapped_column(db.Integer, primary_key=True)

        db = SQLAlchemy(app, model_class=Base)

        class User(db.Model):  # type: ignore[no-redef]
            name: sa_orm.Mapped[str] = sa_orm.mapped_column(db.String)

        class Employee(User):  # type: ignore[no-redef]
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(db.String)

    db.create_all()
    db.session.add(Employee(name="Emp Loyee", title="Admin"))
    db.session.commit()
    user = db.session.execute(db.select(User)).scalar()
    employee = db.session.execute(db.select(Employee)).scalar()
    assert user is not None
    assert employee is not None
    assert user.id == 1
    assert employee.id == 1


@pytest.mark.usefixtures("app_ctx")
def test_abstractmodel(app: Flask, model_class: t.Any) -> None:
    db = SQLAlchemy(app, model_class=model_class)

    if issubclass(db.Model, (sa_orm.MappedAsDataclass)):

        class TimestampModel(db.Model):
            __abstract__ = True
            created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime, nullable=False, insert_default=datetime.utcnow, init=False
            )
            updated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime,
                insert_default=datetime.utcnow,
                onupdate=datetime.utcnow,
                init=False,
            )

        class Post(TimestampModel):
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(
                db.Integer, primary_key=True, init=False
            )
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(db.String, nullable=False)

    elif issubclass(db.Model, (sa_orm.DeclarativeBase, sa_orm.DeclarativeBaseNoMeta)):

        class TimestampModel(db.Model):  # type: ignore[no-redef]
            __abstract__ = True
            created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime, nullable=False, default=datetime.utcnow
            )
            updated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
            )

        class Post(TimestampModel):  # type: ignore[no-redef]
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(db.Integer, primary_key=True)
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(db.String, nullable=False)

    else:

        class TimestampModel(db.Model):  # type: ignore[no-redef]
            __abstract__ = True
            created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
            updated = db.Column(
                db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow
            )

        class Post(TimestampModel):  # type: ignore[no-redef]
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String, nullable=False)

    db.create_all()
    db.session.add(Post(title="Admin Post"))
    db.session.commit()
    post = db.session.execute(db.select(Post)).scalar()
    assert post is not None
    assert post.created is not None
    assert post.updated is not None


@pytest.mark.usefixtures("app_ctx")
def test_mixinmodel(app: Flask, model_class: t.Any) -> None:
    db = SQLAlchemy(app, model_class=model_class)

    if issubclass(db.Model, (sa_orm.MappedAsDataclass)):

        class TimestampMixin(sa_orm.MappedAsDataclass):
            created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime, nullable=False, insert_default=datetime.utcnow, init=False
            )
            updated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime,
                insert_default=datetime.utcnow,
                onupdate=datetime.utcnow,
                init=False,
            )

        class Post(TimestampMixin, db.Model):
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(
                db.Integer, primary_key=True, init=False
            )
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(db.String, nullable=False)

    elif issubclass(db.Model, (sa_orm.DeclarativeBase, sa_orm.DeclarativeBaseNoMeta)):

        class TimestampMixin:  # type: ignore[no-redef]
            created: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime, nullable=False, default=datetime.utcnow
            )
            updated: sa_orm.Mapped[datetime] = sa_orm.mapped_column(
                db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
            )

        class Post(TimestampMixin, db.Model):  # type: ignore[no-redef]
            id: sa_orm.Mapped[int] = sa_orm.mapped_column(db.Integer, primary_key=True)
            title: sa_orm.Mapped[str] = sa_orm.mapped_column(db.String, nullable=False)

    else:

        class TimestampMixin:  # type: ignore[no-redef]
            created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
            updated = db.Column(
                db.DateTime, onupdate=datetime.utcnow, default=datetime.utcnow
            )

        class Post(TimestampMixin, db.Model):  # type: ignore[no-redef]
            id = db.Column(db.Integer, primary_key=True)
            title = db.Column(db.String, nullable=False)

    db.create_all()
    db.session.add(Post(title="Admin Post"))
    db.session.commit()
    post = db.session.execute(db.select(Post)).scalar()
    assert post is not None
    assert post.created is not None
    assert post.updated is not None


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
