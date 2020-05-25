import flask
import pytest

from flask_sqlalchemy import before_models_committed
from flask_sqlalchemy import models_committed

pytestmark = pytest.mark.skipif(
    not flask.signals_available, reason="Signals require the blinker library."
)


@pytest.fixture()
def app(app):
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
    return app


def test_before_committed(app, db, Todo):
    class Namespace:
        is_received = False

    def before_committed(sender, changes):
        Namespace.is_received = True

    before_models_committed.connect(before_committed)
    todo = Todo("Awesome", "the text")
    db.session.add(todo)
    db.session.commit()
    assert Namespace.is_received
    before_models_committed.disconnect(before_committed)


def test_model_signals(db, Todo):
    recorded = []

    def committed(sender, changes):
        assert isinstance(changes, list)
        recorded.extend(changes)

    models_committed.connect(committed)
    todo = Todo("Awesome", "the text")
    db.session.add(todo)
    assert len(recorded) == 0
    db.session.commit()
    assert len(recorded) == 1
    assert recorded[0][0] == todo
    assert recorded[0][1] == "insert"
    del recorded[:]
    todo.text = "aha"
    db.session.commit()
    assert len(recorded) == 1
    assert recorded[0][0] == todo
    assert recorded[0][1] == "update"
    del recorded[:]
    db.session.delete(todo)
    db.session.commit()
    assert len(recorded) == 1
    assert recorded[0][0] == todo
    assert recorded[0][1] == "delete"
    models_committed.disconnect(committed)
