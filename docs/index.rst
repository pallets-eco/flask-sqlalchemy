Flask-SQLAlchemy
================

.. module:: flaskext.sqlalchemy

Flask-SQLAlchemy adds support for `SQLAlchemy`_ to your `Flask`_
application.  This module is currently still under development and the
documentation is lacking.  If you want to get started, have a look at the
`example sourcecode`_.

.. _SQLAlchemy: http://sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/
.. _example sourcecode:
   http://github.com/mitsuhiko/flask-sqlalchemy/tree/master/examples/

API
---

This part of the documentation documents each and every public class or
function from Flask-SQLAlchemy.

Configuration
-------------

.. autoclass:: SQLAlchemy
   :members:

Models
------

.. autoclass:: Model
   :members:

.. autoclass:: BaseQuery
   :members: get, get_or_404, paginate, first_or_404

   .. method:: get(ident)

      Return an instance of the object based on the given identifier
      (primary key), or `None` if not found.

   .. method:: all()

      Return the results represented by this query as a list.  This
      results in an execution of the underlying query.

   .. method:: order_by(*criteron)

      apply one or more ORDER BY criterion to the query and return the
      newly resulting query.

   .. method:: limit(limit)
      
      Apply a LIMIT  to the query and return the newly resulting query.

   .. method:: offset(offset)

      Apply an OFFSET  to the query and return the newly resulting
      query.

   .. method:: first()

      Return the first result of this query or `None` if the result
      doesn’t contain any row.  This results in an execution of the
      underlying query.

.. autoclass:: Pagination
   :members:

Debug Helpers
-------------

.. autofunction:: get_debug_queries
