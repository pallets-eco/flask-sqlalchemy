import sqlalchemy as sa

from flask_sqlalchemy import BaseQuery
from flask_sqlalchemy import SQLAlchemy


def test_sqlalchemy_includes():
    """Various SQLAlchemy objects are exposed as attributes."""
    db = SQLAlchemy()

    assert db.Column == sa.Column

    # The Query object we expose is actually our own subclass.
    assert db.Query == BaseQuery
