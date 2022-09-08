import os

import pytest
import sqlalchemy as sa
import sqlalchemy.pool

from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app_nr(app):
    """Signal/event registration with record queries breaks when
    sqlalchemy.create_engine() is mocked out.
    """
    app.config["SQLALCHEMY_RECORD_QUERIES"] = False
    return app


@pytest.fixture
def nr_app_ctx(app_nr):
    with app_nr.app_context() as ctx:
        yield ctx


class TestConfigKeys:
    def test_default_error_without_uri_or_binds(self, app, recwarn):
        """
        Test that default configuration throws an error because
        SQLALCHEMY_DATABASE_URI and SQLALCHEMY_BINDS are unset
        """

        SQLAlchemy(app)

        # Our pytest fixture for creating the app sets
        # SQLALCHEMY_DATABASE_URI, so undo that here so that we
        # can inspect what FSA does below:
        del app.config["SQLALCHEMY_DATABASE_URI"]

        with pytest.raises(RuntimeError) as exc_info:
            SQLAlchemy(app)

        expected = "Either 'SQLALCHEMY_DATABASE_URI' or 'SQLALCHEMY_BINDS' must be set."
        assert exc_info.value.args[0] == expected

    def test_defaults_with_uri(self, app, recwarn):
        """
        Test default config values when URI is provided, in the order they
        appear in the documentation: https://flask-sqlalchemy.palletsprojects.com/config

        Our pytest fixture for creating the app sets SQLALCHEMY_DATABASE_URI
        """

        SQLAlchemy(app)

        # Expecting no warnings for default config with URI
        assert len(recwarn) == 0

        assert app.config["SQLALCHEMY_BINDS"] == {}
        assert app.config["SQLALCHEMY_ECHO"] is False
        assert app.config["SQLALCHEMY_RECORD_QUERIES"] is None
        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
        assert app.config["SQLALCHEMY_ENGINE_OPTIONS"] == {}

    @pytest.mark.usefixtures("app_ctx")
    def test_engine_creation_ok(self, app):
        """create_engine() isn't called until needed. Make sure we can
        do that without errors or warnings.
        """
        assert SQLAlchemy(app).engine


@pytest.mark.usefixtures("nr_app_ctx")
class TestCreateEngine:
    """Tests for _EngineConnector and SQLAlchemy methods involved in
    setting up the SQLAlchemy engine.
    """

    def test_engine_echo_default(self, app_nr):
        db = SQLAlchemy(app_nr)
        assert not db.engine.echo
        assert not db.engine.pool.echo

    def test_engine_echo_true(self, app_nr):
        app_nr.config["SQLALCHEMY_ECHO"] = True
        db = SQLAlchemy(app_nr)
        assert db.engine.echo
        assert db.engine.pool.echo

    def test_config_from_engine_options(self, app_nr):
        app_nr.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"echo": True}
        assert SQLAlchemy(app_nr).engine.echo

    def test_config_from_init(self, app_nr):
        db = SQLAlchemy(app_nr, engine_options={"echo": True})
        assert db.engine.echo

    def test_pool_class_default(self, app_nr):
        db = SQLAlchemy(app_nr)
        assert isinstance(db.engine.pool, sa.pool.StaticPool)


@pytest.mark.usefixtures("nr_app_ctx")
def test_sqlite_relative_to_instance_path(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    db = SQLAlchemy(app)
    assert db.engine.url.database == os.path.join(app.instance_path, "test.db")
