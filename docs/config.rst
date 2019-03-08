.. currentmodule:: flask_sqlalchemy

Configuration
=============

The following configuration values exist for Flask-SQLAlchemy.
Flask-SQLAlchemy loads these values from your main Flask config which can
be populated in various ways.  Note that some of those cannot be modified
after the engine was created so make sure to configure as early as
possible and to not modify them at runtime.

Configuration Keys
------------------

A list of configuration keys currently understood by the extension:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

================================== =========================================
``SQLALCHEMY_DATABASE_URI``        The database URI that should be used for
                                   the connection.  Examples:

                                   - ``sqlite:////tmp/test.db``
                                   - ``mysql://username:password@server/db``
``SQLALCHEMY_BINDS``               A dictionary that maps bind keys to
                                   SQLAlchemy connection URIs.  For more
                                   information about binds see :ref:`binds`.
``SQLALCHEMY_ECHO``                If set to `True` SQLAlchemy will log all
                                   the statements issued to stderr which can
                                   be useful for debugging.
``SQLALCHEMY_RECORD_QUERIES``      Can be used to explicitly disable or
                                   enable query recording.  Query recording
                                   automatically happens in debug or testing
                                   mode.  See :func:`get_debug_queries` for
                                   more information.
``SQLALCHEMY_NATIVE_UNICODE``      Can be used to explicitly disable native
                                   unicode support.  This is required for
                                   some database adapters (like PostgreSQL
                                   on some Ubuntu versions) when used with
                                   improper database defaults that specify
                                   encoding-less databases.
``SQLALCHEMY_POOL_SIZE``           The size of the database pool.  Defaults
                                   to the engine's default (usually 5)
``SQLALCHEMY_POOL_TIMEOUT``        Specifies the connection timeout in seconds
                                   for the pool.
``SQLALCHEMY_POOL_RECYCLE``        Number of seconds after which a
                                   connection is automatically recycled.
                                   This is required for MySQL, which removes
                                   connections after 8 hours idle by
                                   default.  Note that Flask-SQLAlchemy
                                   automatically sets this to 2 hours if
                                   MySQL is used. Some backends may use a
                                   different default timeout value. For more
                                   information about timeouts see
                                   :ref:`timeouts`.
``SQLALCHEMY_MAX_OVERFLOW``        Controls the number of connections that
                                   can be created after the pool reached
                                   its maximum size.  When those additional
                                   connections are returned to the pool,
                                   they are disconnected and discarded.
``SQLALCHEMY_TRACK_MODIFICATIONS`` If set to ``True``, Flask-SQLAlchemy will
                                   track modifications of objects and emit
                                   signals.  The default is ``None``, which
                                   enables tracking but issues a warning
                                   that it will be disabled by default in
                                   the future.  This requires extra memory
                                   and should be disabled if not needed.
``SQLALCHEMY_ENGINE_OPTIONS``      A dictionary of keyword args to send to
                                   :func:`~sqlalchemy.create_engine`.  See
                                   also ``engine_options`` to :class:`SQLAlchemy`.
================================== =========================================

.. versionadded:: 0.8
   The ``SQLALCHEMY_NATIVE_UNICODE``, ``SQLALCHEMY_POOL_SIZE``,
   ``SQLALCHEMY_POOL_TIMEOUT`` and ``SQLALCHEMY_POOL_RECYCLE``
   configuration keys were added.

.. versionadded:: 0.12
   The ``SQLALCHEMY_BINDS`` configuration key was added.

.. versionadded:: 0.17
   The ``SQLALCHEMY_MAX_OVERFLOW`` configuration key was added.

.. versionadded:: 2.0
   The ``SQLALCHEMY_TRACK_MODIFICATIONS`` configuration key was added.

.. versionchanged:: 2.1
   ``SQLALCHEMY_TRACK_MODIFICATIONS`` will warn if unset.

.. versionchanged:: 2.4
   ``SQLALCHEMY_ENGINE_OPTIONS`` configuration key was added.

Connection URI Format
---------------------

For a complete list of connection URIs head over to the SQLAlchemy
documentation under (`Supported Databases
<http://www.sqlalchemy.org/docs/core/engines.html>`_).  This here shows
some common connection strings.

SQLAlchemy indicates the source of an Engine as a URI combined with
optional keyword arguments to specify options for the Engine. The form of
the URI is::

    dialect+driver://username:password@host:port/database

Many of the parts in the string are optional.  If no driver is specified
the default one is selected (make sure to *not* include the ``+`` in that
case).

Postgres::

    postgresql://scott:tiger@localhost/mydatabase

MySQL::

    mysql://scott:tiger@localhost/mydatabase

Oracle::

    oracle://scott:tiger@127.0.0.1:1521/sidname

SQLite (note that platform path conventions apply)::

    #Unix/Mac (note the four leading slashes)
    sqlite:////absolute/path/to/foo.db
    #Windows (note 3 leading forward slashes and backslash escapes)
    sqlite:///C:\\absolute\\path\\to\\foo.db
    #Windows (alternative using raw string)
    r'sqlite:///C:\absolute\path\to\foo.db'

Using custom MetaData and naming conventions
--------------------------------------------

You can optionally construct the :class:`SQLAlchemy` object with a custom
:class:`~sqlalchemy.schema.MetaData` object.
This allows you to, among other things,
specify a `custom constraint naming convention
<http://docs.sqlalchemy.org/en/latest/core/constraints.html#constraint-naming-conventions>`_
in conjunction with SQLAlchemy 0.9.2 or higher.
Doing so is important for dealing with database migrations (for instance using
`alembic <https://alembic.sqlalchemy.org>`_ as stated
`here <https://alembic.sqlalchemy.org/en/latest/naming.html>`_. Here's an
example, as suggested by the SQLAlchemy docs::

    from sqlalchemy import MetaData
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    convention = {
        "ix": 'ix_%(column_0_label)s',
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
    }

    metadata = MetaData(naming_convention=convention)
    db = SQLAlchemy(app, metadata=metadata)

For more info about :class:`~sqlalchemy.schema.MetaData`,
`check out the official docs on it
<http://docs.sqlalchemy.org/en/latest/core/metadata.html>`_.

.. _timeouts:

Timeouts
--------

Certain database backends may impose different inactive connection timeouts,
which interferes with Flask-SQLAlchemy's connection pooling.

By default, MariaDB is configured to have a 600 second timeout. This often
surfaces hard to debug, production environment only exceptions like ``2013: Lost connection to MySQL server during query``.

If you are using a backend (or a pre-configured database-as-a-service) with a
lower connection timeout, it is recommended that you set
`SQLALCHEMY_POOL_RECYCLE` to a value less than your backend's timeout.



