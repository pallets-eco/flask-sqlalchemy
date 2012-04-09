API
---

.. module:: flask.ext.sqlalchemy

This part of the documentation documents all the public classes and
functions in Flask-SQLAlchemy.

Configuration
`````````````

.. autoclass:: SQLAlchemy
   :members:

   .. attribute:: Query

      The :class:`BaseQuery` class.

Models
``````

.. autoclass:: Model
   :members:

   .. attribute:: __bind_key__

      Optionally declares the bind to use.  `None` refers to the default
      bind.  For more information see :ref:`binds`.

.. autoclass:: BaseQuery
   :members: get, get_or_404, paginate, first_or_404

   .. method:: all()

      Return the results represented by this query as a list.  This
      results in an execution of the underlying query.

   .. method:: order_by(*criterion)

      apply one or more ORDER BY criterion to the query and return the
      newly resulting query.

   .. method:: limit(limit)

      Apply a LIMIT  to the query and return the newly resulting query.

   .. method:: offset(offset)

      Apply an OFFSET  to the query and return the newly resulting
      query.

   .. method:: first()

      Return the first result of this query or `None` if the result
      doesn’t contain any rows.  This results in an execution of the
      underlying query.

Utilities
`````````

.. autoclass:: Pagination
   :members:

.. autofunction:: get_debug_queries
