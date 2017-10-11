Changelog
=========


Version 2.3.2
-------------

Released on October 11, 2017

- Don't mask the parent table for single-table inheritance models. (`#561`_)

.. _#561: https://github.com/mitsuhiko/flask-sqlalchemy/pull/561


Version 2.3.1
-------------

Released on October 5, 2017

- If a model has a table name that matches an existing table in the metadata,
  use that table. Fixes a regression where reflected tables were not picked up
  by models. (`#551`_)
- Raise the correct error when a model has a table name but no primary key.
  (`#556`_)
- Fix ``repr`` on models that don't have an identity because they have not been
  flushed yet. (`#555`_)
- Allow specifying a ``max_per_page`` limit for pagination, to avoid users
  specifying high values in the request args. (`#542`_)
- For ``paginate`` with ``error_out=False``, the minimum value for ``page`` is
  1 and ``per_page`` is 0. (`#558`_)

.. _#542: https://github.com/mitsuhiko/flask-sqlalchemy/pull/542
.. _#551: https://github.com/mitsuhiko/flask-sqlalchemy/pull/551
.. _#555: https://github.com/mitsuhiko/flask-sqlalchemy/pull/555
.. _#556: https://github.com/mitsuhiko/flask-sqlalchemy/pull/556
.. _#558: https://github.com/mitsuhiko/flask-sqlalchemy/pull/558


Version 2.3.0
-------------

Released on September 28, 2017

- Multiple bugs with ``__tablename__`` generation are fixed. Names will be
  generated for models that define a primary key, but not for single-table
  inheritance subclasses. Names will not override a ``declared_attr``.
  ``PrimaryKeyConstraint`` is detected. (`#541`_)
- Passing an existing ``declarative_base()`` as ``model_class`` to
  ``SQLAlchemy.__init__`` will use this as the base class instead of creating
  one. This allows customizing the metaclass used to construct the base.
  (`#546`_)
- The undocumented ``DeclarativeMeta`` internals that the extension uses for
  binds and table name generation have been refactored to work as mixins.
  Documentation is added about how to create a custom metaclass that does not
  do table name generation. (`#546`_)
- Model and metaclass code has been moved to a new ``models`` module.
  ``_BoundDeclarativeMeta`` is renamed to ``DefaultMeta``; the old name will be
  removed in 3.0. (`#546`_)
- Models have a default ``repr`` that shows the model name and primary key.
  (`#530`_)
- Fixed a bug where using ``init_app`` would cause connectors to always use the
  ``current_app`` rather than the app they were created for. This caused issues
  when multiple apps were registered with the extension. (`#547`_)

.. _#530: https://github.com/mitsuhiko/flask-sqlalchemy/pull/530
.. _#541: https://github.com/mitsuhiko/flask-sqlalchemy/pull/541
.. _#546: https://github.com/mitsuhiko/flask-sqlalchemy/pull/546
.. _#547: https://github.com/mitsuhiko/flask-sqlalchemy/pull/547


Version 2.2
-----------

Released on February 27, 2017, codename Dubnium

- Minimum SQLAlchemy version is 0.8 due to use of ``sqlalchemy.inspect``.
- Added support for custom ``query_class`` and ``model_class`` as args
  to the ``SQLAlchemy`` constructor. (`#328`_)
- Allow listening to SQLAlchemy events on ``db.session``. (`#364`_)
- Allow ``__bind_key__`` on abstract models. (`#373`_)
- Allow ``SQLALCHEMY_ECHO`` to be a string. (`#409`_)
- Warn when ``SQLALCHEMY_DATABASE_URI`` is not set. (`#443`_)
- Don't let pagination generate invalid page numbers. (`#460`_)
- Drop support of Flask < 0.10. This means the db session is always tied to
  the app context and its teardown event. (`#461`_)
- Tablename generation logic no longer accesses class properties unless they
  are ``declared_attr``. (`#467`_)

.. _#328: https://github.com/mitsuhiko/flask-sqlalchemy/pull/328
.. _#364: https://github.com/mitsuhiko/flask-sqlalchemy/pull/364
.. _#373: https://github.com/mitsuhiko/flask-sqlalchemy/pull/373
.. _#409: https://github.com/mitsuhiko/flask-sqlalchemy/pull/409
.. _#443: https://github.com/mitsuhiko/flask-sqlalchemy/pull/443
.. _#460: https://github.com/mitsuhiko/flask-sqlalchemy/pull/460
.. _#461: https://github.com/mitsuhiko/flask-sqlalchemy/pull/461
.. _#467: https://github.com/mitsuhiko/flask-sqlalchemy/pull/467

Version 2.1
-----------

Released on October 23rd 2015, codename Caesium

- Table names are automatically generated in more cases, including
  subclassing mixins and abstract models.
- Allow using a custom MetaData object.
- Add support for binds parameter to session.

Version 2.0
-----------

Released on August 29th 2014, codename Bohrium

- Changed how the builtin signals are subscribed to skip non Flask-SQLAlchemy
  sessions.  This will also fix the attribute error about model changes
  not existing.
- Added a way to control how signals for model modifications are tracked.
- Made the ``SignallingSession`` a public interface and added a hook
  for customizing session creation.
- If the ``bind`` parameter is given to the signalling session it will no
  longer cause an error that a parameter is given twice.
- Added working table reflection support.
- Enabled autoflush by default.
- Consider ``SQLALCHEMY_COMMIT_ON_TEARDOWN`` harmful and remove from docs.

Version 1.0
-----------

Released on July 20th 2013, codename Aurum

- Added Python 3.3 support.
- Dropped 2.5 compatibility.
- Various bugfixes
- Changed versioning format to do major releases for each update now.

Version 0.16
------------

- New distribution format (flask_sqlalchemy)
- Added support for Flask 0.9 specifics.

Version 0.15
------------

- Added session support for multiple databases

Version 0.14
------------

- Make relative sqlite paths relative to the application root.

Version 0.13
------------

- Fixed an issue with Flask-SQLAlchemy not selecting the correct binds.

Version 0.12
------------
- Added support for multiple databases.
- Expose Flask-SQLAlchemy's BaseQuery as `db.Query`.
- Set default query_class for `db.relation`, `db.relationship`, and
  `db.dynamic_loader` to Flask-SQLAlchemy's BaseQuery.
- Improved compatibility with Flask 0.7.

Version 0.11
------------

- Fixed a bug introduced in 0.10 with alternative table constructors.

Version 0.10
------------

- Added support for signals.
- Table names are now automatically set from the class name unless
  overriden.
- Model.query now always works for applications directly passed to
  the SQLAlchemy constructor.  Furthermore the property now raises
  an RuntimeError instead of being None.
- added session options to constructor.
- fixed a broken `__repr__`
- `db.Table` is now a factor function that creates table objects.
  This makes it possible to omit the metadata.

Version 0.9
-----------

- applied changes to pass the Flask extension approval process.

Version 0.8
-----------

- added a few configuration keys for creating connections.
- automatically activate connection recycling for MySQL connections.
- added support for the Flask testing mode.

Version 0.7
-----------

- Initial public release
