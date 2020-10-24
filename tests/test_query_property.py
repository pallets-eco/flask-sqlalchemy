import pytest
from werkzeug.exceptions import NotFound


def test_app_bound(db, Todo):
    # If an app was passed to the SQLAlchemy constructor,
    # the query property is always available.
    todo = Todo("Test", "test")
    db.session.add(todo)
    db.session.commit()
    assert len(Todo.query.all()) == 1


def test_get_or_404(Todo):
    with pytest.raises(NotFound):
        Todo.query.get_or_404(1)

    expected = "Expected message"

    with pytest.raises(NotFound) as e_info:
        Todo.query.get_or_404(1, description=expected)

    assert e_info.value.description == expected


def test_first_or_404(Todo):
    with pytest.raises(NotFound):
        Todo.query.first_or_404()

    expected = "Expected message"

    with pytest.raises(NotFound) as e_info:
        Todo.query.first_or_404(description=expected)

    assert e_info.value.description == expected
