.. _binds:

.. currentmodule:: flask.ext.sqlalchemy

Multiple Databases with Binds
=============================

Starting with 0.12 Flask-SQLAlchemy can easily connect to multiple
databases.  To achieve that it preconfigures SQLAlchemy to support
multiple “binds”.

What are binds?  In SQLAlchemy speak a bind is something that can execute
SQL statements and is usually a connection or engine.  In Flask-SQLAlchemy
binds are always engines that are created for you automatically behind the
scenes.  Each of these engines is then associated with a short key (the
bind key).  This key is then used at model declaration time to assocate a
model with a specific engine.

If no bind key is specified for a model the default connection is used
instead (as configured by ``SQLALCHEMY_DATABASE_URI``).

Example Configuration
---------------------

The following configuration declares three database connections.  The
special default one as well as two others named `users` (for the users)
and `appmeta` (which connects to a sqlite database for read only access to
some data the application provides internally)::

    SQLALCHEMY_DATABASE_URI = 'postgres://localhost/main'
    SQLALCHEMY_BINDS = {
        'users':        'mysqldb://localhost/users',
        'appmeta':      'sqlite:////path/to/appmeta.db'
    }

Creating and Dropping Tables
----------------------------

The :meth:`~SQLAlchemy.create_all` and :meth:`~SQLAlchemy.drop_all` methods
by default operate on all declared binds, including the default one.  This
behavior can be customized by providing the `bind` parameter.  It takes
either a single bind name, ``'__all__'`` to refer to all binds or a list
of binds.  The default bind (``SQLALCHEMY_DATABASE_URI``) is named `None`:

>>> db.create_all()
>>> db.create_all(bind=['users'])
>>> db.create_all(bind='appmeta')
>>> db.drop_all(bind=None)

Referring to Binds
------------------

If you declare a model you can specify the bind to use with the
:attr:`~Model.__bind_key__` attribute::

    class User(db.Model):
        __bind_key__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)

Internally the bind key is stored in the table's `info` dictionary as
``'bind_key'``.  This is important to know because when you want to create
a table object directly you will have to put it in there::

    user_favorites = db.Table('user_favorites',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('message_id', db.Integer, db.ForeignKey('message.id')),
        info={'bind_key': 'users'}
    )

If you specified the `__bind_key__` on your models you can use them exactly the
way you are used to.  The model connects to the specified database connection 
itself.
