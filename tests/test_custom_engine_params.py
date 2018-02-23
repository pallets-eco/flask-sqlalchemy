import pytest
import flask_sqlalchemy as fsa


def test_set_engine_params(app):
    db = fsa.SQLAlchemy(app, engine_params={'pool_pre_ping': True})
    options = dict()
    db.apply_engine_params(app, options)

    assert options['pool_pre_ping'] is True


def test_set_engine_params_overrides_defaults(app):
    db = fsa.SQLAlchemy(app, engine_params={'max_overflow': 20})
    options = dict()
    db.apply_engine_params(app, options)

    assert options['max_overflow'] == 20


def test_set_engine_params_wrong_param(app):
    db = fsa.SQLAlchemy(app, engine_params={'wrong': 20})

    with pytest.raises(TypeError):
        db.engine
