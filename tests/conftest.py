from datetime import datetime

import flask
import pytest
from click.testing import CliRunner

import sqlalchemy
import flask_sqlalchemy as fsa


@pytest.fixture
def app(request):
    app = flask.Flask(request.module.__name__)
    app.testing = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_BINDS'] = {
        'users': 'mysqldb://localhost/users',
        'geo':   'postgres://localhost/geo',
    }
    return app


@pytest.fixture
def db(app):
    return fsa.SQLAlchemy(app)


@pytest.fixture
def Todo(db):
    class Todo(db.Model):
        __tablename__ = 'todos'
        id = db.Column('todo_id', db.Integer, primary_key=True)
        title = db.Column(db.String(60))
        text = db.Column(db.String)
        done = db.Column(db.Boolean)
        pub_date = db.Column(db.DateTime)

        def __init__(self, title, text):
            self.title = title
            self.text = text
            self.done = False
            self.pub_date = datetime.utcnow()
    db.create_all()
    yield Todo
    db.drop_all()


@pytest.fixture
def clirunner():
    return CliRunner()


@pytest.fixture
def script_info(app, db):
    try:
        from flask.cli import ScriptInfo
    except ImportError:
        from flask_cli import ScriptInfo

    return ScriptInfo(create_app=lambda x: app)


@pytest.fixture(autouse=True)
def mock_engines(mocker):
    """Mock all SQLAlchemy engines, except SQLite
    (which requires no dependencies"""
    real_create_engine = sqlalchemy.create_engine
    real_EngineDebuggingSignalEvents = fsa._EngineDebuggingSignalEvents

    def mock_create_engine(info, **options):
        # sqlite has no dependencies, so we won't mock it
        if info.drivername == 'sqlite':
            return real_create_engine(info, **options)
        # every other engine has dependencies, so we'll mock them
        return mocker.Mock(name="{} engine".format(info.drivername))

    def mock_debugging_signals(engine, import_name):
        if isinstance(engine, mocker.Mock):
            return mocker.Mock(name=engine._mock_name + " debugging signals")
        return real_EngineDebuggingSignalEvents(engine, import_name)

    mocker.patch(
        'flask_sqlalchemy.sqlalchemy.create_engine',
        mock_create_engine,
    )
    mocker.patch(
        'flask_sqlalchemy._EngineDebuggingSignalEvents',
        mock_debugging_signals,
    )
