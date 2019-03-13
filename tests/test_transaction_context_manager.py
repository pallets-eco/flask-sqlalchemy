import random

import pytest
from sqlalchemy import event
from sqlalchemy.exc import InvalidRequestError

import flask_sqlalchemy as fsa


def fix_pysqlite(engine):
    """This ugly mess is a known issue with pysqlite and how it does
    Serializable isolation / Savepoints / Transactional DDL:
    http://docs.sqlalchemy.org/en/rel_1_0/dialects/sqlite.html#pysqlite-serializable
    """

    @event.listens_for(engine, "connect")
    def do_connect(dbapi_connection, connection_record):
        # disable pysqlite's emitting of the BEGIN statement entirely.
        # also stops it from emitting COMMIT before any DDL.
        dbapi_connection.isolation_level = None

    @event.listens_for(engine, "begin")
    def do_begin(conn):
        # emit our own BEGIN
        conn.execute("BEGIN")


@pytest.fixture(params=(True, False), ids=('nested transaction', 'savepoint'))
def app(app, request):
    app.config['SQLALCHEMY_NESTED_TRANSACTION'] = request.param
    return app


@pytest.fixture(params=(True, False), ids=('autocommit', 'no autocommit'))
def db(app, request):
    db = fsa.SQLAlchemy(app, session_options={'autocommit': request.param})
    fix_pysqlite(db.engine)
    return db


def new_todo(Todo, db):
    todo = Todo(str(random.random()), str(random.random()))
    db.session.add(todo)
    return todo


def assert_the_same(todo1, todo2):
    assert todo1.title, todo2.title
    assert todo1.text, todo2.text
    assert todo1.pub_date, todo2.pub_date


def test_commit(Todo, db):
    with db.transaction():
        todo = new_todo(Todo, db)
    db.session.rollback()
    assert_the_same(todo, Todo.query.one())


def test_rollback(Todo, db):
    def method():
        with db.transaction():
            new_todo(Todo, db)
            return 1 / 0
    with pytest.raises(ZeroDivisionError):
        method()
    if not db.session().autocommit:
        db.session.commit()
    assert len(Todo.query.all()) == 0


def test_rollback_explicitly(Todo, db):
    def method():
        with db.transaction():
            new_todo(Todo, db)
            raise fsa.Rollback()
    with pytest.raises(fsa.Rollback):
        method()
    with db.transaction():
        todo = new_todo(Todo, db)
    assert_the_same(todo, Todo.query.one())


def test_rollback_no_propagate(Todo, db):
    def method():
        with db.transaction():
            new_todo(Todo, db)
            raise fsa.Rollback(propagate=False)
    method()
    with db.transaction():
        todo = new_todo(Todo, db)
    assert_the_same(todo, Todo.query.one())


def test_no_isolate_transaction(app, Todo, db):
    app.config['SQLALCHEMY_ISOLATE_TRANSACTION'] = False
    todo0 = new_todo(Todo, db)
    with db.transaction():
        todo1 = new_todo(Todo, db)
    db.session.rollback()
    r = Todo.query.order_by(Todo.id).all()
    assert_the_same(todo0, r[0])
    assert_the_same(todo1, r[1])


def test_explicitly_isolate_transaction(app, Todo, db):
    app.config['SQLALCHEMY_ISOLATE_TRANSACTION'] = False
    todo0 = new_todo(Todo, db)
    with db.transaction(isolate=True):
        todo1 = new_todo(Todo, db)
    db.session.rollback()
    if db.session().autocommit:
        r = Todo.query.order_by(Todo.id).all()
        assert_the_same(todo0, r[0])
        assert_the_same(todo1, r[1])
    else:
        assert_the_same(todo1, Todo.query.one())


def test_config_isolate_transaction(app, Todo, db):
    app.config['SQLALCHEMY_ISOLATE_TRANSACTION'] = True
    todo0 = new_todo(Todo, db)
    with db.transaction():
        todo1 = new_todo(Todo, db)
    db.session.rollback()
    if db.session().autocommit:
        r = Todo.query.order_by(Todo.id).all()
        assert_the_same(todo0, r[0])
        assert_the_same(todo1, r[1])
    else:
        assert_the_same(todo1, Todo.query.one())


def test_subtransactions_two_commits(Todo, db):
    with db.transaction():
        todo0 = new_todo(Todo, db)
        with db.transaction():
            todo1 = new_todo(Todo, db)
        todo2 = new_todo(Todo, db)
    db.session.rollback()
    r = Todo.query.order_by(Todo.id).all()
    assert_the_same(todo0, r[0])
    assert_the_same(todo1, r[1])
    assert_the_same(todo2, r[2])


def test_subtransactions_inner_rollback(app, Todo, db):
    todos = []

    def method():
        with db.transaction():
            todos.append(new_todo(Todo, db))
            try:
                with db.transaction():
                    todos.append(new_todo(Todo, db))
                    return 1 / 0
            except ZeroDivisionError:
                pass
            todos.append(new_todo(Todo, db))

    if app.config['SQLALCHEMY_NESTED_TRANSACTION']:
        method()
        r = Todo.query.order_by(Todo.id).all()
        assert_the_same(todos[0], r[0])
        assert_the_same(todos[2], r[1])
    else:
        with pytest.raises(InvalidRequestError):
            method()
        with db.transaction():
            todo = new_todo(Todo, db)
        assert_the_same(todo, Todo.query.one())


def test_subtransactions_inner_manual_rollback_silently(app, Todo, db):
    todos = []

    def method():
        with db.transaction():
            todos.append(new_todo(Todo, db))
            with db.transaction():
                todos.append(new_todo(Todo, db))
                raise fsa.Rollback(propagate=False)
            todos.append(new_todo(Todo, db))
    if app.config['SQLALCHEMY_NESTED_TRANSACTION']:
        method()
        r = Todo.query.order_by(Todo.id).all()
        assert_the_same(todos[0], r[0])
        assert_the_same(todos[2], r[1])
    else:
        with pytest.raises(InvalidRequestError):
            method()
        with db.transaction():
            todo = new_todo(Todo, db)
        assert_the_same(todo, Todo.query.one())


def test_subtransactions_inner_manual_rollback_loudly(Todo, db):
    def method():
        with db.transaction():
            new_todo(Todo, db)
            with db.transaction():
                new_todo(Todo, db)
                raise fsa.Rollback(propagate=True)
            new_todo(Todo, db)
    with pytest.raises(fsa.Rollback):
        method()
    with db.transaction():
        todo = new_todo(Todo, db)
    assert_the_same(todo, Todo.query.one())


def test_subtransactions_inner_manual_rollback(app, Todo, db):
    todos = []

    def method():
        with db.transaction():
            todos.append(new_todo(Todo, db))
            with db.transaction():
                todos.append(new_todo(Todo, db))
                raise fsa.Rollback()
            todos.append(new_todo(Todo, db))
    if app.config['SQLALCHEMY_NESTED_TRANSACTION']:
        method()
        r = Todo.query.order_by(Todo.id).all()
        assert_the_same(todos[0], r[0])
        assert_the_same(todos[2], r[1])
    else:
        with pytest.raises(fsa.Rollback):
            method()
        with db.transaction():
            todo = new_todo(Todo, db)
        assert_the_same(todo, Todo.query.one())


def test_subtransactions_outer_rollback(Todo, db):
    def method():
        with db.transaction():
            new_todo(Todo, db)
            with db.transaction():
                new_todo(Todo, db)
            new_todo(Todo, db)
            return 1 / 0
    with pytest.raises(ZeroDivisionError):
        method()
    with db.transaction():
        todo = new_todo(Todo, db)
    assert_the_same(todo, Todo.query.one())


def test_local(Todo, db):
    assert db.tx_local is None
    assert db.root_tx_local is None
    with db.transaction(base=0, val=1):
        assert db.tx_local is db.root_tx_local
        assert db.tx_local['base'] == 0
        assert db.tx_local['val'] == 1
        with db.transaction(base=0, val=2):
            assert db.tx_local is not db.root_tx_local
            assert db.root_tx_local['base'] == 0
            assert db.root_tx_local['val'] == 1
            assert db.tx_local['base'] == 0
            assert db.tx_local['val'] == 2
        assert db.tx_local is db.root_tx_local
        assert db.tx_local['base'] == 0
        assert db.tx_local['val'] == 1
    assert db.tx_local is None
    assert db.root_tx_local is None
