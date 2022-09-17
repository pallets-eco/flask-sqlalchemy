API
===


Extension
---------

.. module:: flask_sqlalchemy

.. autoclass:: SQLAlchemy
    :members:


Model
-----

.. module:: flask_sqlalchemy.model

.. autoclass:: Model
    :members:

    .. attribute:: __bind_key__

        Use this bind key to select a metadata and engine to associate with this model's
        table. Ignored if ``metadata`` or ``__table__`` is set. If not given, uses the
        default key, ``None``.

    .. attribute:: __tablename__

        The name of the table in the database. This is required by SQLAlchemy; however,
        Flask-SQLAlchemy will set it automatically if a model has a primary key defined.
        If the ``__table__`` or ``__tablename__`` is set explicitly, that will be used
        instead.

.. autoclass:: DefaultMeta

.. autoclass:: BindMetaMixin

.. autoclass:: NameMetaMixin


Query
-----

.. module:: flask_sqlalchemy.query

.. autoclass:: Query
    :members:


Session
-------

.. module:: flask_sqlalchemy.session

.. autoclass:: Session
    :members:


Pagination
----------

.. module:: flask_sqlalchemy.pagination

.. autoclass:: Pagination
    :members:


Record Queries
--------------

.. module:: flask_sqlalchemy.record_queries

.. autofunction:: get_recorded_queries


Track Modifications
-------------------

.. module:: flask_sqlalchemy.track_modifications

.. autodata:: models_committed
    :no-value:

.. autodata:: before_models_committed
    :no-value:
