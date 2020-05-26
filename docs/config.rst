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
``SQLALCHEMY_ENGINE_OPTIONS``      A dictionary of keyword args to send to
                                   :func:`~sqlalchemy.create_engine`.  See
                                   also ``engine_options`` to :class:`SQLAlchemy`.
================================== =========================================

.. versionchanged:: 3.0
    ``SQLALCHEMY_TRACK_MODIFICATIONS`` defaults to ``False``.

.. versionchanged:: 3.0
    ``SQLALCHEMY_DATABASE_URI`` no longer defaults to
    ``'sqlite:///:memory:'``

.. versionchanged:: 3.0
    Removed ``SQLALCHEMY_NATIVE_UNICODE``, ``SQLALCHEMY_POOL_SIZE``,
    ``SQLALCHEMY_POOL_TIMEOUT``, ``SQLALCHEMY_POOL_RECYCLE``, and
    ``SQLALCHEMY_MAX_OVERFLOW``.

.. versionchanged:: 3.0
    Deprecated ``SQLALCHEMY_COMMIT_ON_TEARDOWN``.

.. versionadded:: 2.4
    Added ``SQLALCHEMY_ENGINE_OPTIONS``.

.. versionchanged:: 2.4
    Deprecated ``SQLALCHEMY_NATIVE_UNICODE``, ``SQLALCHEMY_POOL_SIZE``,
    ``SQLALCHEMY_POOL_TIMEOUT``, ``SQLALCHEMY_POOL_RECYCLE``, and
    ``SQLALCHEMY_MAX_OVERFLOW``.

.. versionadded:: 2.0
    Added ``SQLALCHEMY_TRACK_MODIFICATIONS``.

.. versionadded:: 0.17
    Added ``SQLALCHEMY_MAX_OVERFLOW``.

.. versionadded:: 0.12
    Added ``SQLALCHEMY_BINDS``.

.. versionadded:: 0.8
    Added ``SQLALCHEMY_NATIVE_UNICODE``, ``SQLALCHEMY_POOL_SIZE``,
    ``SQLALCHEMY_POOL_TIMEOUT`` and ``SQLALCHEMY_POOL_RECYCLE``.


Connection URI Format
---------------------

For a complete list of connection URIs head over to the SQLAlchemy
documentation under (`Supported Databases
<https://docs.sqlalchemy.org/en/latest/core/engines.html>`_).  This here shows
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
<https://docs.sqlalchemy.org/en/latest/core/constraints.html#constraint-naming-conventions>`_
in conjunction with SQLAlchemy 0.9.2 or higher.
Doing so is important for dealing with database migrations (for instance using
`alembic <https://alembic.sqlalchemy.org/en/latest/>`_ as stated
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
<https://docs.sqlalchemy.org/en/latest/core/metadata.html>`_.

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
