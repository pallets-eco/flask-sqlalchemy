import pytest

import flask_sqlalchemy as fsa


def test_no_app_bound(app):
    db = fsa.SQLAlchemy()
    db.init_app(app)

    class Foo(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    # If no app is bound to the SQLAlchemy instance, a
    # request context is required to access Model.query.
    pytest.raises(RuntimeError, getattr, Foo, 'query')
    with app.test_request_context():
        db.create_all()
        foo = Foo()
        db.session.add(foo)
        db.session.commit()
        assert len(Foo.query.all()) == 1


def test_app_bound(db, Todo):
    # If an app was passed to the SQLAlchemy constructor,
    # the query property is always available.
    todo = Todo('Test', 'test')
    db.session.add(todo)
    db.session.commit()
    assert len(Todo.query.all()) == 1
