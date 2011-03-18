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

=============================== =========================================
``SQLALCHEMY_DATABASE_URI``     The database URI that should be used for
                                the connection.  Examples:

                                - ``sqlite:////tmp/test.db``
                                - ``mysql://username:password@server/db``
``SQLALCHEMY_BINDS``            A dictionary that maps bind keys to
                                SQLAlchemy connection URIs.  For more
                                information about binds see :ref:`binds`.
``SQLALCHEMY_ECHO``             If set to `True` SQLAlchemy will log all
                                the statements issued to stderr which can
                                be useful for debugging.
``SQLALCHEMY_RECORD_QUERIES``   Can be used to explicitly disable or
                                enable query recording.  Query recording
                                automatically happens in debug or testing
                                mode.  See :func:`get_debug_queries` for
                                more information.
``SQLALCHEMY_NATIVE_UNICODE``   Can be used to explicitly disable native
                                unicode support.  This is required for
                                some database adapters (like PostgreSQL
                                on some Ubuntu versions) when used with
                                inproper database defaults that specify
                                encoding-less databases.
``SQLALCHEMY_POOL_SIZE``        The size of the database pool.  Defaults
                                to the engine's default (usually 5)
``SQLALCHEMY_POOL_TIMEOUT``     Specifies the connection timeout for the
                                pool.  Defaults to 10.
``SQLALCHEMY_POOL_RECYCLE``     Number of seconds after which a
                                connection is automatically recycled.
                                This is required for MySQL, which removes
                                connections after 8 hours idle by
                                default.  Note that Flask-SQLAlchemy
                                automatically sets this to 2 hours if
                                MySQL is used.
=============================== =========================================

.. versionadded:: 0.8
   The ``SQLALCHEMY_NATIVE_UNICODE``, ``SQLALCHEMY_POOL_SIZE``,
   ``SQLALCHEMY_POOL_TIMEOUT`` and ``SQLALCHEMY_POOL_RECYCLE``
   configuration keys were added.

.. versionadded:: 0.12
   The ``SQLALCHEMY_BINDS`` configuration key was added.

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

SQLite (note the four leading slashes)::

    sqlite:////absolute/path/to/foo.db
