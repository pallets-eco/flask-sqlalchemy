import flask
import pytest

import flask_sqlalchemy as fsa
import sqlalchemy as sa


pytestmark = pytest.mark.skipif(
    not flask.signals_available,
    reason='Signals require the blinker library.'
)


@pytest.fixture()
def app(app):
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    return app


@pytest.fixture()
def db(db):
    # required for correct handling of nested transactions, see
    # https://docs.sqlalchemy.org/en/rel_1_0/dialects/sqlite.html#serializable-isolation-savepoints-transactional-ddl
    @sa.event.listens_for(db.engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    @sa.event.listens_for(db.engine, "begin")
    def do_begin(conn):
        # emit our own BEGIN
        conn.execute("BEGIN")

    return db


def test_before_committed(app, db, Todo):
    class Namespace(object):
        is_received = False

    def before_committed(sender, changes):
        Namespace.is_received = True

    fsa.before_models_committed.connect(before_committed)
    todo = Todo('Awesome', 'the text')
    db.session.add(todo)
    db.session.commit()
    assert Namespace.is_received
    fsa.before_models_committed.disconnect(before_committed)


def test_model_signals(db, Todo):
    recorded = []

    def committed(sender, changes):
        assert isinstance(changes, list)
        recorded.extend(changes)

    fsa.models_committed.connect(committed)
    todo = Todo('Awesome', 'the text')
    db.session.add(todo)
    assert len(recorded) == 0
    db.session.commit()
    assert len(recorded) == 1
    assert recorded[0][0] == todo
    assert recorded[0][1] == 'insert'
    del recorded[:]
    todo.text = 'aha'
    db.session.commit()
    assert len(recorded) == 1
    assert recorded[0][0] == todo
    assert recorded[0][1] == 'update'
    del recorded[:]
    db.session.delete(todo)
    db.session.commit()
    assert len(recorded) == 1
    assert recorded[0][0] == todo
    assert recorded[0][1] == 'delete'
    fsa.models_committed.disconnect(committed)


def test_model_signals_nested_transaction(db, Todo):
    before_commit_recorded = []
    commit_recorded = []

    def before_committed(sender, changes):
        before_commit_recorded.extend(changes)

    def committed(sender, changes):
        commit_recorded.extend(changes)

    fsa.before_models_committed.connect(before_committed)
    fsa.models_committed.connect(committed)
    with db.session.begin_nested():
        todo = Todo('Awesome', 'the text')
        db.session.add(todo)
        try:
            with db.session.begin_nested():
                todo2 = Todo('Bad', 'to rollback')
                db.session.add(todo2)
                raise Exception('raising to roll back')
        except Exception:
            pass
    assert before_commit_recorded == []
    assert commit_recorded == []
    db.session.commit()
    assert before_commit_recorded == [(todo, 'insert')]
    assert commit_recorded == [(todo, 'insert')]
    del before_commit_recorded[:]
    del commit_recorded[:]
    try:
        with db.session.begin_nested():
            todo = Todo('Great', 'the text')
            db.session.add(todo)
            with db.session.begin_nested():
                todo2 = Todo('Bad', 'to rollback')
                db.session.add(todo2)
                raise Exception('raising to roll back')
    except Exception:
        pass
    assert before_commit_recorded == []
    assert commit_recorded == []
    db.session.commit()
    assert before_commit_recorded == []
    assert commit_recorded == []
    fsa.before_models_committed.disconnect(before_committed)
    fsa.models_committed.disconnect(committed)
