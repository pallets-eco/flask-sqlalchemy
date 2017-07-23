# -*- coding: utf-8 -*-
"""
    flask_sqlalchemy.cli
    ~~~~~~~~~~~~~~~~~~~~

    Command Line Interface for managing the database.

    :copyright: (c) 2017 by David Baumgold.
    :license: MIT, see LICENSE for more details.
"""

from __future__ import absolute_import

from functools import wraps

import click
from flask import current_app
from werkzeug.local import LocalProxy

try:
    from flask.cli import with_appcontext
except ImportError:
    from flask_cli import with_appcontext

state = LocalProxy(lambda: current_app.extensions['sqlalchemy'])


def commit(fn):
    """Decorator to commit changes after the command is run."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        fn(*args, **kwargs)
        state.db.session.commit()
    return wrapper


@click.group()
def db():
    """Manages the database."""


@db.command('create')
@click.option('--bind', default='__all__')
@with_appcontext
@commit
def db_create(bind):
    """Creates database tables."""
    state.db.create_all(bind=bind)
    click.secho('Database created successfully.', fg='green')


@db.command('drop')
@click.option('--bind', default='__all__')
@click.confirmation_option(prompt=(
    "This will destroy all the data in your database. "
    "Do you want to continue?"
))
@with_appcontext
@commit
def db_drop(bind):
    """Drops database tables."""
    state.db.drop_all(bind=bind)
    click.secho('Database dropped successfully.', fg='green')
