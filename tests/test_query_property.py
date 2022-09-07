import pytest
from werkzeug.exceptions import NotFound

from flask_sqlalchemy import SQLAlchemy


def test_app_ctx_required(app):
    db = SQLAlchemy()
    db.init_app(app)

    class Foo(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    with pytest.raises(RuntimeError):
        assert Foo.query

    with app.test_request_context():
        db.create_all()
        foo = Foo()
        db.session.add(foo)
        db.session.commit()
        assert len(Foo.query.all()) == 1


@pytest.mark.usefixtures("app_ctx")
def test_get_or_404(Todo):
    with pytest.raises(NotFound):
        Todo.query.get_or_404(1)

    expected = "Expected message"

    with pytest.raises(NotFound) as e_info:
        Todo.query.get_or_404(1, description=expected)

    assert e_info.value.description == expected


@pytest.mark.usefixtures("app_ctx")
def test_first_or_404(Todo):
    with pytest.raises(NotFound):
        Todo.query.first_or_404()

    expected = "Expected message"

    with pytest.raises(NotFound) as e_info:
        Todo.query.first_or_404(description=expected)

    assert e_info.value.description == expected
