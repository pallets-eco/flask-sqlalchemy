Configuration
=============


Configuration Keys
------------------

Configuration is loaded from the Flask ``app.config`` when :meth:`.SQLAlchemy.init_app`
is called. The configuration is not read again after that. Therefore, all configuration
must happen before initializing the application.

.. module:: flask_sqlalchemy.config

.. data:: SQLALCHEMY_DATABASE_URI

    The database connection URI used for the default engine. It can be either a string
    or a SQLAlchemy ``URL`` instance. See below and :external:doc:`core/engines` for
    examples.

    At least one of this and :data:`SQLALCHEMY_BINDS` must be set.

    .. versionchanged:: 3.0
        No longer defaults to an in-memory SQLite database if not set.

.. data:: SQLALCHEMY_ENGINE_OPTIONS

    A dict of arguments to pass to :func:`sqlalchemy.create_engine` for the default
    engine.

    This takes precedence over the ``engine_options`` argument to :class:`.SQLAlchemy`,
    which can be used to set default options for all engines.

    .. versionchanged:: 3.0
        Only applies to the default bind.

    .. versionadded:: 2.4

.. data:: SQLALCHEMY_BINDS

    A dict mapping bind keys to engine options. The value can be a string or a
    SQLAlchemy ``URL`` instance. Or it can be a dict of arguments, including the ``url``
    key, that will be passed to :func:`sqlalchemy.create_engine`. The ``None`` key can
    be used to configure the default bind, but :data:`SQLALCHEMY_ENGINE_OPTIONS` and
    :data:`SQLALCHEMY_DATABASE_URI` take precedence.

    At least one of this and :data:`SQLALCHEMY_DATABASE_URI` must be set.

    .. versionadded:: 0.12

.. data:: SQLALCHEMY_ECHO

    The default value for ``echo`` and ``echo_pool`` for every engine. This is useful to
    quickly debug the connections and queries issued from SQLAlchemy.

    .. versionchanged:: 3.0
        Sets ``echo_pool`` in addition to ``echo``.

.. data:: SQLALCHEMY_RECORD_QUERIES

    If enabled, information about each query during a request will be recorded. Use
    :func:`.get_recorded_queries` to get a list of queries that were issued during the
    request.

    .. versionchanged:: 3.0
        Not enabled automatically in debug or testing mode.

.. data:: SQLALCHEMY_TRACK_MODIFICATIONS

    If enabled, all ``insert``, ``update``, and ``delete`` operations on models are
    recorded, then sent in :data:`.models_committed` and
    :data:`.before_models_committed` signals when ``session.commit()`` is called.

    This adds a significant amount of overhead to every session. Prefer using
    SQLAlchemy's :external:doc:`orm/events` directly for the exact information you need.

    .. versionchanged:: 3.0
        Disabled by default.

    .. versionadded:: 2.0

.. versionchanged:: 3.1
    Removed ``SQLALCHEMY_COMMIT_ON_TEARDOWN``.

.. versionchanged:: 3.0
    Removed ``SQLALCHEMY_NATIVE_UNICODE``, ``SQLALCHEMY_POOL_SIZE``,
    ``SQLALCHEMY_POOL_TIMEOUT``, ``SQLALCHEMY_POOL_RECYCLE``, and
    ``SQLALCHEMY_MAX_OVERFLOW``.


Connection URL Format
---------------------

See SQLAlchemy's documentation on :external:doc:`core/engines` for a complete
description of syntax, dialects, and options.

A basic database connection URL uses the following format. Username, password, host, and
port are optional depending on the database type and configuration.

.. code-block:: text

    dialect://username:password@host:port/database

Here are some example connection strings:

.. code-block:: text

    # SQLite, relative to Flask instance path
    sqlite:///project.db

    # PostgreSQL
    postgresql://scott:tiger@localhost/project

    # MySQL / MariaDB
    mysql://scott:tiger@localhost/project

SQLite does not use a user or host, so its URLs always start with _three_ slashes
instead of two. The ``dbname`` value is a file path. Absolute paths start with a
_fourth_ slash (on Linux or Mac). Relative paths are relative to the Flask application's
:attr:`~flask.Flask.instance_path`.


Default Driver Options
----------------------

Some default options are set for SQLite and MySQL engines to make them more usable by
default in web applications.

SQLite relative file paths are relative to the Flask instance path instead of the
current working directory. In-memory databases use a static pool and
``check_same_thread`` to work across requests.

MySQL (and MariaDB) servers are configured to drop connections that have been idle for
8 hours, which can result in an error like ``2013: Lost connection to MySQL server
during query``. A default ``pool_recycle`` value of 2 hours (7200 seconds) is used to
recreate connections before that timeout.


Engine Configuration Precedence
-------------------------------

Because Flask-SQLAlchemy has support for multiple engines, there are rules for which
config overrides other config. Most applications will only have a single database and
only need to use :data:`SQLALCHEMY_DATABASE_URI` and :data:`SQLALCHEMY_ENGINE_OPTIONS`.

-   If the ``engine_options`` argument is given to :class:`.SQLAlchemy`, it sets default
    options for *all* engines. :data:`SQLALCHEMY_ECHO` sets the default value for both
    ``echo`` and ``echo_pool`` for all engines.
-   The options for each engine in :data:`.SQLALCHEMY_BINDS` override those defaults.
-   :data:`.SQLALCHEMY_ENGINE_OPTIONS` overrides the ``None`` key in
    ``SQLALCHEMY_BINDS``, and :data:`.SQLALCHEMY_DATABASE_URI` overrides the ``url`` key
    in that engine's options.


Using custom MetaData and naming conventions
--------------------------------------------

You can optionally construct the :class:`.SQLAlchemy` object with a custom
:class:`~sqlalchemy.schema.MetaData` object. This allows you to specify a custom
constraint `naming convention`_. This makes constraint names consistent and predictable,
useful when using migrations, as described by `Alembic`_.

.. code-block:: python

    from sqlalchemy import MetaData
    from flask_sqlalchemy import SQLAlchemy

    db = SQLAlchemy(metadata=MetaData(naming_convention={
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }))

.. _naming convention: https://docs.sqlalchemy.org/core/constraints.html#constraint-naming-conventions
.. _Alembic: https://alembic.sqlalchemy.org/en/latest/naming.html


Timeouts
--------

Certain databases may be configured to close inactive connections after a period of
time. MySQL and MariaDB are configured for this by default, but database services may
also configure this type of limit. This can result in an error like
``2013: Lost connection to MySQL server during query``.

If you encounter this error, try setting ``pool_recycle`` in the engine options to
a value less than the database's timeout.

Alternatively, you can try setting ``pool_pre_ping`` if you expect the database to close
connections often, such as if it's running in a container that may restart.

See SQAlchemy's docs on `dealing with disconnects`_ for more information.

.. _dealing with disconnects: https://docs.sqlalchemy.org/core/pooling.html#dealing-with-disconnects
