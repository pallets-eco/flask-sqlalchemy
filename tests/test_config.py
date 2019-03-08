import flask_sqlalchemy as fsa

import mock
import pytest


class TestConfigKeys:

    def test_defaults(self, app):
        """
        Test all documented config values in the order they appear in our
        documentation: http://flask-sqlalchemy.pocoo.org/dev/config/
        """
        # Our pytest fixture for creating the app sets
        # SQLALCHEMY_TRACK_MODIFICATIONS, so we undo that here so that we
        # can inspect what FSA does below:
        del app.config['SQLALCHEMY_TRACK_MODIFICATIONS']

        with pytest.warns(fsa.FSADeprecationWarning) as records:
            fsa.SQLAlchemy(app)

        # Only expecting one warning for the track modifications deprecation.
        assert len(records) == 1

        assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
        assert app.config['SQLALCHEMY_BINDS'] is None
        assert app.config['SQLALCHEMY_ECHO'] is False
        assert app.config['SQLALCHEMY_RECORD_QUERIES'] is None
        assert app.config['SQLALCHEMY_NATIVE_UNICODE'] is None
        assert app.config['SQLALCHEMY_POOL_SIZE'] is None
        assert app.config['SQLALCHEMY_POOL_TIMEOUT'] is None
        assert app.config['SQLALCHEMY_POOL_RECYCLE'] is None
        assert app.config['SQLALCHEMY_MAX_OVERFLOW'] is None
        assert app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] is None
        assert app.config['SQLALCHEMY_ENGINE_OPTIONS'] == {}

    def test_track_modifications_warning(self, app, recwarn):

        # pytest fixuture sets SQLALCHEMY_TRACK_MODIFICATIONS = False
        fsa.SQLAlchemy(app)

        # So we shouldn't have any warnings
        assert len(recwarn) == 0

        # Let's trigger the warning
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = None
        fsa.SQLAlchemy(app)

        # and verify it showed up as expected
        assert len(recwarn) == 1
        expect = 'SQLALCHEMY_TRACK_MODIFICATIONS adds significant overhead' \
                 ' and will be disabled by default in the future.  Set it' \
                 ' to True or False to suppress this warning.'
        assert recwarn[0].message.args[0] == expect

    def test_uri_binds_warning(self, app, recwarn):
        # Let's trigger the warning
        del app.config['SQLALCHEMY_DATABASE_URI']
        fsa.SQLAlchemy(app)

        # and verify it showed up as expected
        assert len(recwarn) == 1
        expect = 'Neither SQLALCHEMY_DATABASE_URI nor SQLALCHEMY_BINDS' \
                 ' is set. Defaulting SQLALCHEMY_DATABASE_URI to'\
                 ' "sqlite:///:memory:".'
        assert recwarn[0].message.args[0] == expect


@pytest.fixture
def app_nr(app):
    """
        Signal/event registration with record queries breaks when
        sqlalchemy.create_engine() is mocked out.
    """
    app.config['SQLALCHEMY_RECORD_QUERIES'] = False
    return app


@mock.patch.object(fsa.sqlalchemy, 'create_engine', autospec=True, spec_set=True)
class TestCreateEngine:
    """
        Tests for _EngineConnector and SQLAlchemy methods inolved in setting up
        the SQLAlchemy engine.
    """

    def test_engine_echo_default(self, m_create_engine, app_nr):
        fsa.SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert 'echo' not in options

    def test_engine_echo_true(self, m_create_engine, app_nr):
        app_nr.config['SQLALCHEMY_ECHO'] = True
        fsa.SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert options['echo'] is True

    def test_convert_unicode_default(self, m_create_engine, app_nr):
        fsa.SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert options['convert_unicode'] is True

    def test_config_from_engine_options(self, m_create_engine, app_nr):
        app_nr.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'foo': 'bar'}
        fsa.SQLAlchemy(app_nr).get_engine()

        args, options = m_create_engine.call_args
        assert options['foo'] == 'bar'

    def test_config_from_init(self, m_create_engine, app_nr):
        fsa.SQLAlchemy(app_nr, engine_options={'bar': 'baz'}).get_engine()

        args, options = m_create_engine.call_args
        assert options['bar'] == 'baz'
