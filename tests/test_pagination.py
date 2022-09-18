from __future__ import annotations

import typing as t

import pytest
from flask import Flask
from werkzeug.exceptions import NotFound

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.pagination import Pagination


def _make_page(
    *, page: int = 1, per_page: int = 10, total: int | None = 150
) -> Pagination:
    return Pagination(query=None, page=page, per_page=per_page, total=total, items=[])


def test_first_page() -> None:
    p = _make_page()
    assert p.page == 1
    assert p.per_page == 10
    assert p.total == 150
    assert p.pages == 15
    assert not p.has_prev
    assert p.prev_num is None
    assert p.has_next
    assert p.next_num == 2


def test_last_page() -> None:
    p = _make_page(page=15)
    assert p.page == 15
    assert p.has_prev
    assert p.prev_num == 14
    assert not p.has_next
    assert p.next_num is None


def test_item_numbers_first_page() -> None:
    p = _make_page()
    p.items = list(range(10))
    assert p.first == 1
    assert p.last == 10


def test_item_numbers_last_page() -> None:
    p = _make_page(page=15)
    p.items = list(range(5))
    assert p.first == 141
    assert p.last == 145


def test_item_numbers_0() -> None:
    p = _make_page(total=0)
    assert p.first == 0
    assert p.last == 0


@pytest.mark.parametrize(
    ("per_page", "total"),
    [
        (10, 0),
        (10, None),
    ],
)
def test_0_pages(per_page: int, total: int | None) -> None:
    p = _make_page(per_page=per_page, total=total)
    assert p.pages == 0
    assert not p.has_prev
    assert not p.has_next


@pytest.mark.parametrize(
    ("page", "expect"),
    [
        (1, [1, 2, 3, 4, 5, None, 14, 15]),
        (2, [1, 2, 3, 4, 5, 6, None, 14, 15]),
        (3, [1, 2, 3, 4, 5, 6, 7, None, 14, 15]),
        (4, [1, 2, 3, 4, 5, 6, 7, 8, None, 14, 15]),
        (5, [1, 2, 3, 4, 5, 6, 7, 8, 9, None, 14, 15]),
        (6, [1, 2, None, 4, 5, 6, 7, 8, 9, 10, None, 14, 15]),
        (7, [1, 2, None, 5, 6, 7, 8, 9, 10, 11, None, 14, 15]),
        (8, [1, 2, None, 6, 7, 8, 9, 10, 11, 12, None, 14, 15]),
        (9, [1, 2, None, 7, 8, 9, 10, 11, 12, 13, 14, 15]),
        (10, [1, 2, None, 8, 9, 10, 11, 12, 13, 14, 15]),
        (11, [1, 2, None, 9, 10, 11, 12, 13, 14, 15]),
        (12, [1, 2, None, 10, 11, 12, 13, 14, 15]),
        (13, [1, 2, None, 11, 12, 13, 14, 15]),
        (14, [1, 2, None, 12, 13, 14, 15]),
        (15, [1, 2, None, 13, 14, 15]),
    ],
)
def test_iter_pages(page: int, expect: list[int | None]) -> None:
    p = _make_page(page=page)
    assert list(p.iter_pages()) == expect


def test_iter_0_pages() -> None:
    p = _make_page(total=0)
    assert list(p.iter_pages()) == []


@pytest.mark.parametrize("page", [1, 2, 3, 4])
def test_iter_pages_short(page: int) -> None:
    p = _make_page(page=page, total=40)
    assert list(p.iter_pages()) == [1, 2, 3, 4]


class _PaginateCallable:
    def __init__(self, app: Flask, Todo: t.Any) -> None:
        self.app = app
        self.Todo = Todo

    def __call__(
        self,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = None,
        error_out: bool = True,
        count: bool = True,
    ) -> Pagination:
        with self.app.test_request_context(
            query_string={"page": page, "per_page": per_page}
        ):
            return self.Todo.query.paginate(  # type: ignore[no-any-return]
                max_per_page=max_per_page, error_out=error_out, count=count
            )


@pytest.fixture
def paginate(app: Flask, db: SQLAlchemy, Todo: t.Any) -> _PaginateCallable:
    with app.app_context():
        for i in range(1, 101):
            db.session.add(Todo(title=f"task {i}"))

        db.session.commit()

    return _PaginateCallable(app, Todo)


def test_paginate(paginate: _PaginateCallable) -> None:
    p = paginate()
    assert p.page == 1
    assert p.per_page == 20
    assert len(p.items) == 20
    assert p.total == 100
    assert p.pages == 5


def test_paginate_qs(paginate: _PaginateCallable) -> None:
    p = paginate(page=2, per_page=10)
    assert p.page == 2
    assert p.per_page == 10


def test_paginate_max(paginate: _PaginateCallable) -> None:
    p = paginate(per_page=100, max_per_page=50)
    assert p.per_page == 50


def test_no_count(paginate: _PaginateCallable) -> None:
    p = paginate(count=False)
    assert p.total is None


@pytest.mark.parametrize(
    ("page", "per_page"), [("abc", None), (None, "abc"), (0, None), (None, -1)]
)
def test_error_out(paginate: _PaginateCallable, page: t.Any, per_page: t.Any) -> None:
    with pytest.raises(NotFound):
        paginate(page=page, per_page=per_page)


@pytest.mark.usefixtures("app_ctx")
def test_no_items_404(Todo: t.Any) -> None:
    p = Todo.query.paginate()
    assert len(p.items) == 0

    with pytest.raises(NotFound):
        Todo.query.paginate(page=2)
