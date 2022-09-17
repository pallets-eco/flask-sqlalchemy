Multiple Databases with Binds
=============================

SQLAlchemy can connect to more than one database at a time. It refers to different
engines as "binds". Flask-SQLAlchemy simplifies how binds work by associating each
engine with a short string, a "bind key", and then associating each model and table with
a bind key. The session will choose what engine to use for a query based on the bind key
of the thing being queried. If no bind key is given, the default engine is used.


Configuring Binds
-----------------

The default bind is still configured by setting :data:`.SQLALCHEMY_DATABASE_URI`, and
:data:`.SQLALCHEMY_ENGINE_OPTIONS` for any engine options. Additional binds are given in
:data:`.SQLALCHEMY_BINDS`, a dict mapping bind keys to engine URLs. To specify engine
options for a bind, the value can be a dict of engine options with the ``"url"`` key,
instead of only a URL string.

.. code-block:: python

    SQLALCHEMY_DATABASE_URI = "postgresql:///main"
    SQLALCHEMY_BINDS = {
        "meta": "sqlite:////path/to/meta.db",
        "auth": {
            "url": "mysql://localhost/users",
            "pool_recycle": 3600,
        },
    }


Defining Models and Tables with Binds
-------------------------------------

Flask-SQLAlchemy will create a metadata and engine for each configured bind. Models and
tables with a bind key will be registered with the corresponding metadata, and the
session will query them using the corresponding engine.

To set the bind for a model, set the ``__bind_key__`` class attribute. Not setting a
bind key is equivalent to setting it to ``None``, the default key.

.. code-block:: python

    class User(db.Model):
        __bind_key__ = "auth"
        id = db.Column(db.Integer, primary_key=True)

Models that inherit from this model will share the same bind key, or can override it.

To set the bind for a table, pass the ``bind_key`` keyword argument.

.. code-block:: python

    user_table = db.Table(
        "user",
        db.Column("id", db.Integer, primary_key=True),
        bind_key="auth",
    )

Ultimately, the session looks up the bind key on the metadata associated with the model
or table. That association happens during creation. Therefore, changing the bind key
after creating a model or table will have no effect.


Accessing Metadata and Engines
------------------------------

You may need to inspect the metadata or engine for a bind. Note that you should execute
queries through the session, not directly on the engine.

The default engine is :attr:`.SQLAlchemy.engine`, and the default metadata is
:attr:`.SQLAlchemy.metadata`. :attr:`.SQLAlchemy.engines` and
:attr:`.SQLAlchemy.metadatas` are dicts mapping all bind keys.


Creating and Dropping Tables
----------------------------

The :meth:`~.SQLAlchemy.create_all` and :meth:`~.SQLAlchemy.drop_all` methods operate on
all binds by default. The ``bind_key`` argument to these methods can be a string or
``None`` to operate on a single bind, or a list of strings or ``None`` to operate on a
subset of binds. Because these methods access the engines, they must be called inside an
application context.

.. code-block:: python

    # create tables for all binds
    db.create_all()

    # create tables for the default and "auth" binds
    db.create_all(bind=[None, "auth"])

    # create tables for the "meta" bind
    db.create_all(bind="meta")

    # drop tables for the default bind
    db.drop_all(bind=None)
