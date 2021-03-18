import os
from unittest import mock

import pytest
import sqlalchemy
from sqlalchemy.pool import NullPool

from flask_sqlalchemy import SQLAlchemy


@pytest.fixture
def app_nr(app):
    """Signal/event registration with record queries breaks when
    sqlalchemy.create_engine() is mocked out.
    """
    app.config["SQLALCHEMY_RECORD_QUERIES"] = False
    return app


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

        expected = "Either SQLALCHEMY_DATABASE_URI or SQLALCHEMY_BINDS needs to be set."
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

        assert app.config["SQLALCHEMY_BINDS"] is None
        assert app.config["SQLALCHEMY_ECHO"] is False
        assert app.config["SQLALCHEMY_RECORD_QUERIES"] is None
        assert app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] is False
        assert app.config["SQLALCHEMY_ENGINE_OPTIONS"] == {}

    def test_engine_creation_ok(self, app):
        """create_engine() isn't called until needed. Make sure we can
        do that without errors or warnings.
        """
        assert SQLAlchemy(app).get_engine()


@mock.patch.object(sqlalchemy, "create_engine", autospec=True, spec_set=True)
class TestCreateEngine:
    """Tests for _EngineConnector and SQLAlchemy methods involved in
    setting up the SQLAlchemy engine.
    """

    def test_engine_echo_default(self, m_create_engine, app_nr):
        SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert "echo" not in options

    def test_engine_echo_true(self, m_create_engine, app_nr):
        app_nr.config["SQLALCHEMY_ECHO"] = True
        SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert options["echo"] is True

    def test_config_from_engine_options(self, m_create_engine, app_nr):
        app_nr.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"foo": "bar"}
        SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert options["foo"] == "bar"

    def test_config_from_init(self, m_create_engine, app_nr):
        SQLAlchemy(app_nr, engine_options={"bar": "baz"}).get_engine()

        args, options = m_create_engine.call_args
        assert options["bar"] == "baz"

    def test_pool_class_default(self, m_create_engine, app_nr):
        SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert options["poolclass"].__name__ == "StaticPool"

    def test_pool_class_nullpool(self, m_create_engine, app_nr):
        engine_options = {"poolclass": NullPool}
        SQLAlchemy(app_nr, engine_options=engine_options).get_engine()

        args, options = m_create_engine.call_args
        assert options["poolclass"].__name__ == "NullPool"
        assert "pool_size" not in options


def test_sqlite_relative_to_app_root(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    db = SQLAlchemy(app)
    assert db.engine.url.database == os.path.join(app.root_path, "test.db")
