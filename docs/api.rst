API
---

.. module:: flask_sqlalchemy

Configuration
`````````````

.. autoclass:: SQLAlchemy
   :members:

Models
``````

.. autoclass:: Model
    :members:

    .. attribute:: __bind_key__

        Optionally declares the bind to use. ``None`` refers to the default
        bind. For more information see :ref:`binds`.

    .. attribute:: __tablename__

        The name of the table in the database. This is required by SQLAlchemy;
        however, Flask-SQLAlchemy will set it automatically if a model has a
        primary key defined. If the ``__table__`` or ``__tablename__`` is set
        explicitly, that will be used instead.

.. autoclass:: BaseQuery
    :members:

Sessions
````````

.. autoclass:: SignallingSession
    :members:

Utilities
`````````

.. autoclass:: Pagination
    :members:

.. autofunction:: get_debug_queries
