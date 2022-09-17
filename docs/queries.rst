Modifying and Querying Data
===========================


Insert, Update, Delete
----------------------

See SQLAlchemy's `ORM tutorial`_ and other SQLAlchemy documentation for more information
about modifying data with the ORM.

.. _ORM tutorial: https://docs.sqlalchemy.org/tutorial/orm_data_manipulation.html

To insert data, pass the model object to ``db.session.add()``:

.. code-block:: python

    user = User()
    db.session.add(user)
    db.session.commit()

To update data, modify attributes on the model objects:

.. code-block:: python

    user.verified = True
    db.session.commit()

To delete data, pass the model object to ``db.session.delete()``:

.. code-block:: python

    db.session.delete(user)
    db.session.commit()

After modifying data, you must call ``db.session.commit()`` to commit the changes to
the database. Otherwise, they will be discarded at the end of the request.


Select
------

See SQLAlchemy's `Querying Guide`_ and other SQLAlchemy documentation for more
information about querying data with the ORM.

.. _Querying Guide: https://docs.sqlalchemy.org/orm/queryguide.html

Queries are executed through ``db.session.execute()``. They can be constructed
using :func:`~sqlalchemy.sql.expression.select`. Executing a select returns a
:class:`~sqlalchemy.engine.Result` object that has many methods for working with the
returned rows.

.. code-block:: python

    user = db.session.execute(db.select(User).filter_by(username=username)).one()


Legacy Query Interface
----------------------

.. warning::
    SQLAlchemy 2.0 has designated the ``Query`` interface as "legacy". It will no
    longer be updated and may be deprecated in the future. Prefer using
    ``db.session.execute(db.select(...))`` instead.

Flask-SQLAlchemy adds a ``query`` object to each model. This can be used to query
instances of a given model. ``User.query`` is a shortcut for ``db.session.query(User)``.

.. code-block:: python

    # get the user with id 5
    user = User.query.get(5)

    # get a user by username
    user = User.query.filter_by(username=username).one()


Queries for Views
`````````````````

If you write a Flask view function it's often useful to return a ``404 Not Found`` error
for missing entries. Flask-SQLAlchemy provides some extra query methods.

-   :meth:`.Query.get_or_404` will raise a 404 if the row with the given id doesn't
    exist, otherwise it will return the instance.
-   :meth:`.Query.first_or_404` will raise a 404 if the query does not return any
    results, otherwise it will return the first result.
-   :meth:`.Query.one_or_404` will raise a 404 if the query does not return exactly one
    result, otherwise it will return the result.

.. code-block:: python

    @app.route("/user/<username>")
    def show_user(username):
        user = User.query.filter_by(username=username).one_or_404()
        return render_template("show_user.html", user=user)

You can add a custom message to the 404 error:

    .. code-block:: python

        user = User.query.filter_by(username=username).one_or_404(
            description=f"No user named '{username}'."
        )
