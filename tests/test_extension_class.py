from flask_sqlalchemy import SQLAlchemy


def test_constructor_sets_app(app):
    db = SQLAlchemy(app)

    assert db.app is not None


def test_init_app_sets_app(app):
    db = SQLAlchemy()
    db.init_app(app)

    assert db.app is not None
