Flask-SQLAlchemy
================

.. module:: flaskext.sqlalchemy

Flask-SQLAlchemy adds support for `SQLAlchemy`_ to your `Flask`_
application.  This module is currently still under development and the
documentation is lacking.  If you want to get started, have a look at the
`example sourcecode`_.

.. _SQLAlchemy: http://www.sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/
.. _example sourcecode:
   http://github.com/mitsuhiko/flask-sqlalchemy/tree/master/examples/

Installation
------------

Install the extension with one of the following commands::

    $ easy_install Flask-SQLAlchemy

or alternatively if you have pip installed::

    $ pip install Flask-SQLAlchemy


How to Use
----------

Flask-SQLAlchemy is fun to use, and incredibly easy for basic applications.
For the complete guide, checkout out the API
documentation on the :class:`SQLAlchemy` class.

Basically all you have to do is to create an :class:`SQLAlchemy` object
and use this to declare models.  Here is a complete example::

    from flask import Flask
    from flaskext.sqlalchemy import SQLAlchemy
    from werkzeug import generate_password_hash, check_password_hash
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db = SQLAlchemy(app)


    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)
        pw_hash = db.Column(db.String(80))

        def __init__(self, username, password):
            self.username = username
            self.set_password(password)

        def set_password(self, password):
            self.pw_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.pw_hash, password)

        def __repr__(self):
            return '<User %r>' % self.username

To create the initial database, just import the `db` object from a
interactive Python shell and run the :meth:`~SQLAlchemy.create_all` method
to create the tables and database:

>>> from yourapplication import db
>>> db.create_all()

Boom, and there is your database.  Now to create some users:

>>> from yourapplication import User
>>> admin = User('admin', 'open sesame')
>>> guest = User('guest', 'i-shall-pass')

But they are not yet in the database, so let's make sure they are:

>>> db.session.add(admin)
>>> db.session.add(guest)
>>> db.session.commit()

And how do you get the data back? Firstly, because we are not inside the WSGI
application, but using the Python shell we are missing the request context
that is required for accessing the query method for models. So lets set up
a dummy request context for our shell:

>>> from yourapplication import app
>>> app.test_request_context().push()

And now, accessing the data in database is easy as a pie:

>>> users = User.query.all()
[<User u'admin'>, <User u'guest'>]
>>> admin = User.query.filter_by(username='admin').first()
<User u'admin'>

.. versionchanged:: 0.10
   The `__tablename__` attribute is now optional.  If not defined, the
   class name (converted to lowercase and camel cased words separated
   by underscores) is used.

Road to Enlightenment
---------------------

The only things you need to know compared to plain SQLAlchemy are:

1.  :class:`SQLAlchemy` gives you access to the following things:

    -   all the functions and classes from :mod:`sqlalchemy` and
        :mod:`sqlalchemy.orm`
    -   a preconfigured scoped session called `session`
    -   the `metadata`
    -   a :meth:`SQLAlchemy.create_all` and :meth:`SQLAlchemy.drop_all`
        methods to create and drop tables according to the models.
    -   a :class:`Model` baseclass that is a configured declarative base.

2.  The :class:`Model` declarative base class behaves like a regular
    Python class but has a `query` attribute attached that can be used to
    query the model.  (:class:`Model` and :class:`BaseQuery`)

3.  You have to commit the session, but you don't have to remove it at
    the end of the request, Flask-SQLAlchemy does that for you.

4.  In general it behaves as a declarative base system, for everything
    else, just look at the SQLAlchemy documentation.

Configuration Values
--------------------

The following configuration values exist for Flask-SQLAlchemy:

.. tabularcolumns:: |p{6.5cm}|p{8.5cm}|

=============================== =========================================
``SQLALCHEMY_DATABASE_URI``     The database URI that should be used for
                                the connection.  Examples:

                                - ``sqlite:////tmp/test.db``
                                - ``mysql://username:password@server/db``
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

Signalling Support
------------------

.. versionadded:: 0.10

Starting with Flask-SQLAlchemy 0.10 you can now connect to signals to get
notifications when certain things happen.

The following two signals exist:

.. data:: models_committed

   This signal is sent when changed models where committed to the
   database.  The sender is the application that emitted the changes
   and the models and an operation identifier are passed as list of tuples
   in the form ``(model, operation)`` to the receiver in the `changes`
   parameter.

   The model is the instance of the model that was sent to the database
   and the operation is ``'insert'`` when a model was inserted,
   ``'delete'`` when the model was deleted and ``'update'`` if any
   of the columns where updated.

.. data:: before_models_committed

   Works exactly the same as :data:`models_committed` but is emitted
   right before the committing takes place.

API
---

This part of the documentation documents all the public classes and
functions in Flask-SQLAlchemy.

Configuration
`````````````

.. autoclass:: SQLAlchemy
   :members:

Models
``````

.. autoclass:: Model
   :members:

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

.. include:: ../CHANGES
