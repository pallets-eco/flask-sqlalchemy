Version 3.0.0
-------------

Unreleased

-   Drop support for Python 2, 3.4, 3.5, and 3.6.
-   Bump minimum version of Flask to 2.2.
-   Bump minimum version of SQLAlchemy to 1.4.18.
-   Remove previously deprecated code.
-   The ``CamelCase`` to ``snake_case`` table name converter handles more patterns
    correctly. If such a that was was already created in the database changed, either
    use Alembic to rename the table, or set ``__tablename__`` to keep the old name.
    :issue:`406`
-   Set ``SQLALCHEMY_TRACK_MODIFICATIONS`` to ``False`` by default. :pr:`727`
-   Remove default ``'sqlite:///:memory:'`` setting for ``SQLALCHEMY_DATABASE_URI``,
    raise error when both it and ``SQLALCHEMY_BINDS`` are unset. :pr:`731`
-   Configuring SQLite with a relative path is relative to ``app.instance_path`` instead
    of ``app.root_path``. The instance folder is created if necessary. :issue:`462`
-   Deprecate ``SQLALCHEMY_COMMIT_ON_TEARDOWN`` as it can cause various design issues
    that are difficult to debug. Call ``db.session.commit()`` directly instead.
    :issue:`216`
-   Change the default MySQL character set to "utf8mb4". :issue:`875`
-   ``Pagination``, ``Pagination.iter_pages``, and ``Query.paginate`` parameters are
    keyword-only.
-   ``Pagination`` is iterable, iterating over its items. :issue:`70`
-   ``Pagination.apply_to_query`` can be used instead of ``query.paginate``.
-   ``Query.paginate`` ``count`` is more efficient.
-   ``Pagination.iter_pages`` is more efficient. :issue:`622`
-   ``Pagination.iter_pages`` ``right_current`` parameter is inclusive.
-   ``Query`` is renamed from ``BaseQuery``.
-   ``Query.one_or_404`` is added.
-   ``get_debug_queries`` is renamed to ``get_recorded_queries`` to better match the
    config and functionality.
-   Recorded query info is a dataclass instead of a tuple. The ``context`` attribute is
    renamed to ``location``. Finding the location uses a more inclusive check.
-   The ``SQLAlchemy`` extension object uses ``__getattr__`` to alias names from the
    SQLAlchemy package, rather than copying them as attributes.
-   The query class is applied to ``backref`` in ``relationship``. :issue:`417`
-   ``SignallingSession`` is renamed to ``Session``.
-   ``Session.get_bind`` more closely matches the base implementation.
-   ``Model`` ``repr`` distinguishes between transient and pending instances.
    :issue:`967`
-   Different bind keys use different SQLAlchemy ``MetaData`` registries, allowing
    tables in different databases to have the same name. Bind keys are stored and looked
    up on the resulting metadata rather than the model or table.
-   The ``engine_options`` parameter is applied as defaults before per-engine
    configuration.
-   ``SQLALCHEMY_BINDS`` values can either be an engine URL, or a dict of engine options
    including URL, for each bind. ``SQLALCHEMY_DATABASE_URI`` and
    ``SQLALCHEMY_ENGINE_OPTIONS`` correspond to the ``None`` key and take precedence.
    :issue:`783`
-   Engines are created when calling ``init_app`` rather than the first time they are
    accessed. :issue:`698`
-   The extension instance is stored directly as ``app.extensions["sqlalchemy"]``.
    :issue:`698`
-   All parameters except ``app`` are keyword-only.
-   Setup methods that create the engines and session are renamed with a leading
    underscore. They are considered internal interfaces which may change at any time.
-   ``db.Table`` is a subclass instead of a function.
-   The session class can be customized by passing the ``class_`` key in the
    ``session_options`` parameter. :issue:`327`
-   SQLite engines do not use ``NullPool`` if ``pool_size`` is 0.
-   MySQL engines do not set ``pool_size`` to 10.
-   ``db.engines`` exposes the map of bind keys to engines for the current app.
-   ``get_engine``, ``get_tables_for_bind``, and ``get_binds`` are deprecated.
-   Renamed the ``bind`` parameter to ``bind_key`` and removed the ``app`` parameter
    from various methods.
-   ``SQLALCHEMY_RECORD_QUERIES`` configuration takes precedence over ``app.debug`` and
    ``app.testing``, allowing it to be disabled in those modes.
-   The session is scoped to the current app context instead of the thread. This
    requires that an app context is active. This ensures that the session is cleaned up
    after every request.
-   A custom model class can implement ``__init_subclass__`` with class parameters.
    :issue:`1002`
-   An active Flask application context is always required to access ``session`` and
    ``engine``, regardless of if an application was passed to the constructor.
    :issue:`508, 944`


Version 2.5.1
-------------

Released 2021-03-18

-   Fix compatibility with Python 2.7.


Version 2.5.0
-------------

Released 2021-03-18

-   Update to support SQLAlchemy 1.4.
-   SQLAlchemy ``URL`` objects are immutable. Some internal methods have
    changed to return a new URL instead of ``None``. :issue:`885`


Version 2.4.4
-------------

Released 2020-07-14

-   Change base class of meta mixins to ``type``. This fixes an issue
    caused by a regression in CPython 3.8.4. :issue:`852`


Version 2.4.3
-------------

Released 2020-05-26

-   Deprecate ``SQLALCHEMY_COMMIT_ON_TEARDOWN`` as it can cause various
    design issues that are difficult to debug. Call
    ``db.session.commit()`` directly instead. :issue:`216`


Version 2.4.2
-------------

Released 2020-05-25

-   Fix bad pagination when records are de-duped. :pr:`812`


Version 2.4.1
-------------

Released 2019-09-24

-   Fix ``AttributeError`` when using multiple binds with polymorphic
    models. :pr:`651`


Version 2.4.0
-------------

Released 2019-04-24

-   Make engine configuration more flexible. (:pr:`684`)
-   Address SQLAlchemy 1.3 deprecations. (:pr:`684`)
-   ``get_or_404()`` and ``first_or_404()`` now accept a ``description``
    parameter to control the 404 message. (:issue:`636`)
-   Use ``time.perf_counter`` for Python 3 on Windows. (:issue:`638`)
-   Drop support for Python 2.6 and 3.3. (:pr:`687`)
-   Add an example of Flask's tutorial project, Flaskr, adapted for
    Flask-SQLAlchemy. (:pr:`720`)


Version 2.3.2
-------------

Released 2017-10-11

-   Don't mask the parent table for single-table inheritance models.
    (:pr:`561`)


Version 2.3.1
-------------

Released 2017-10-05

-   If a model has a table name that matches an existing table in the
    metadata, use that table. Fixes a regression where reflected tables
    were not picked up by models. (:issue:`551`)
-   Raise the correct error when a model has a table name but no primary
    key. (:pr:`556`)
-   Fix ``repr`` on models that don't have an identity because they have
    not been flushed yet. (:issue:`555`)
-   Allow specifying a ``max_per_page`` limit for pagination, to avoid
    users specifying high values in the request args. (:pr:`542`)
-   For ``paginate`` with ``error_out=False``, the minimum value for
    ``page`` is 1 and ``per_page`` is 0. (:issue:`558`)


Version 2.3.0
-------------

Released 2017-09-28

-   Multiple bugs with ``__tablename__`` generation are fixed. Names
    will be generated for models that define a primary key, but not for
    single-table inheritance subclasses. Names will not override a
    ``declared_attr``. ``PrimaryKeyConstraint`` is detected.
    (:pr:`541`)
-   Passing an existing ``declarative_base()`` as ``model_class`` to
    ``SQLAlchemy.__init__`` will use this as the base class instead of
    creating one. This allows customizing the metaclass used to
    construct the base. (:issue:`546`)
-   The undocumented ``DeclarativeMeta`` internals that the extension
    uses for binds and table name generation have been refactored to
    work as mixins. Documentation is added about how to create a custom
    metaclass that does not do table name generation. (:issue:`546`)
-   Model and metaclass code has been moved to a new ``models`` module.
    ``_BoundDeclarativeMeta`` is renamed to ``DefaultMeta``; the old
    name will be removed in 3.0. (:issue:`546`)
-   Models have a default ``repr`` that shows the model name and primary
    key. (:pr:`530`)
-   Fixed a bug where using ``init_app`` would cause connectors to
    always use the ``current_app`` rather than the app they were created
    for. This caused issues when multiple apps were registered with the
    extension. (:pr:`547`)


Version 2.2
-----------

Released 2017-02-27, codename Dubnium

-   Minimum SQLAlchemy version is 0.8 due to use of
    ``sqlalchemy.inspect``.
-   Added support for custom ``query_class`` and ``model_class`` as args
    to the ``SQLAlchemy`` constructor. (:pr:`328`)
-   Allow listening to SQLAlchemy events on ``db.session``.
    (:pr:`364`)
-   Allow ``__bind_key__`` on abstract models. (:pr:`373`)
-   Allow ``SQLALCHEMY_ECHO`` to be a string. (:issue:`409`)
-   Warn when ``SQLALCHEMY_DATABASE_URI`` is not set. (:pr:`443`)
-   Don't let pagination generate invalid page numbers. (:issue:`460`)
-   Drop support of Flask < 0.10. This means the db session is always
    tied to the app context and its teardown event. (:issue:`461`)
-   Tablename generation logic no longer accesses class properties
    unless they are ``declared_attr``. (:issue:`467`)


Version 2.1
-----------

Released 2015-10-23, codename Caesium

-   Table names are automatically generated in more cases, including
    subclassing mixins and abstract models.
-   Allow using a custom MetaData object.
-   Add support for binds parameter to session.


Version 2.0
-----------

Released 2014-08-29, codename Bohrium

-   Changed how the builtin signals are subscribed to skip
    non-Flask-SQLAlchemy sessions. This will also fix the attribute
    error about model changes not existing.
-   Added a way to control how signals for model modifications are
    tracked.
-   Made the ``SignallingSession`` a public interface and added a hook
    for customizing session creation.
-   If the ``bind`` parameter is given to the signalling session it will
    no longer cause an error that a parameter is given twice.
-   Added working table reflection support.
-   Enabled autoflush by default.
-   Consider ``SQLALCHEMY_COMMIT_ON_TEARDOWN`` harmful and remove from
    docs.


Version 1.0
-----------

Released 2013-07-20, codename Aurum

-   Added Python 3.3 support.
-   Dropped 2.5 compatibility.
-   Various bugfixes
-   Changed versioning format to do major releases for each update now.


Version 0.16
------------

-   New distribution format (flask_sqlalchemy)
-   Added support for Flask 0.9 specifics.


Version 0.15
------------

-   Added session support for multiple databases.


Version 0.14
------------

-   Make relative sqlite paths relative to the application root.


Version 0.13
------------

-   Fixed an issue with Flask-SQLAlchemy not selecting the correct
    binds.


Version 0.12
------------

-   Added support for multiple databases.
-   Expose ``BaseQuery`` as ``db.Query``.
-   Set default ``query_class`` for ``db.relation``,
    ``db.relationship``, and ``db.dynamic_loader`` to ``BaseQuery``.
-   Improved compatibility with Flask 0.7.


Version 0.11
------------

-   Fixed a bug introduced in 0.10 with alternative table constructors.


Version 0.10
------------

-   Added support for signals.
-   Table names are now automatically set from the class name unless
    overridden.
-   ``Model.query`` now always works for applications directly passed to
    the ``SQLAlchemy`` constructor. Furthermore the property now raises
    a ``RuntimeError`` instead of being ``None``.
-   Added session options to constructor.
-   Fixed a broken ``__repr__``.
-   ``db.Table`` is now a factory function that creates table objects.
    This makes it possible to omit the metadata.


Version 0.9
-----------

-   Applied changes to pass the Flask extension approval process.


Version 0.8
-----------

-   Added a few configuration keys for creating connections.
-   Automatically activate connection recycling for MySQL connections.
-   Added support for the Flask testing mode.


Version 0.7
-----------

-   Initial public release
