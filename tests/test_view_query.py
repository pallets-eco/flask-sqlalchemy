from __future__ import annotations

import typing as t

import pytest
import sqlalchemy as sa
import sqlalchemy.orm as sa_orm
from flask import Flask
from werkzeug.exceptions import NotFound

from flask_sqlalchemy import SQLAlchemy


@pytest.mark.usefixtures("app_ctx")
def test_view_get_or_404(db: SQLAlchemy, Todo: t.Any) -> None:
    item = Todo()
    db.session.add(item)
    db.session.commit()
    assert db.get_or_404(Todo, 1) is item
    with pytest.raises(NotFound):
        assert db.get_or_404(Todo, 2)


@pytest.mark.usefixtures("app_ctx")
def test_first_or_404(db: SQLAlchemy, Todo: t.Any) -> None:
    db.session.add(Todo(title="a"))
    db.session.commit()
    result = db.first_or_404(db.select(Todo).filter_by(title="a"))
    assert result.title == "a"

    with pytest.raises(NotFound):
        db.first_or_404(db.select(Todo).filter_by(title="b"))


@pytest.mark.usefixtures("app_ctx")
def test_view_one_or_404(db: SQLAlchemy, Todo: t.Any) -> None:
    db.session.add(Todo(title="a"))
    db.session.add(Todo(title="b"))
    db.session.add(Todo(title="b"))
    db.session.commit()
    result = db.one_or_404(db.select(Todo).filter_by(title="a"))
    assert result.title == "a"

    with pytest.raises(NotFound):
        # MultipleResultsFound
        db.one_or_404(db.select(Todo).filter_by(title="b"))

    with pytest.raises(NotFound):
        # NoResultFound
        db.one_or_404(db.select(Todo).filter_by(title="c"))


@pytest.mark.usefixtures("app_ctx")
def test_paginate(db: SQLAlchemy, Todo: t.Any) -> None:
    db.session.add_all(Todo() for _ in range(150))
    db.session.commit()
    p = db.paginate(db.select(Todo))
    assert p.total == 150
    assert len(p.items) == 20
    p2 = p.next()
    assert p2.page == 2
    assert p2.total == 150


# This test creates its own inline model so that it can use that as the type
@pytest.mark.usefixtures("app_ctx")
def test_view_get_or_404_typed(db: SQLAlchemy, app: Flask) -> None:
    # Copied and pasted from conftest.py
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

    db.create_all()

    todo = Todo()
    todo.title = "Python"
    db.session.add(todo)
    db.session.commit()
    result = db.get_or_404(Todo, 1)
    assert result.title == "Python"
    assert result is todo
    if hasattr(t, "assert_type"):
        t.assert_type(result, Todo)
    with pytest.raises(NotFound):
        assert db.get_or_404(Todo, 2)
    db.drop_all()
