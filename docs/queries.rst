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

    users = db.session.execute(db.select(User).order_by(User.username)).scalars()


Queries for Views
-----------------

If you write a Flask view function it's often useful to return a ``404 Not Found`` error
for missing entries. Flask-SQLAlchemy provides some extra query methods.

-   :meth:`.SQLAlchemy.get_or_404` will raise a 404 if the row with the given id doesn't
    exist, otherwise it will return the instance.
-   :meth:`.SQLAlchemy.first_or_404` will raise a 404 if the query does not return any
    results, otherwise it will return the first result.
-   :meth:`.SQLAlchemy.one_or_404` will raise a 404 if the query does not return exactly
    one result, otherwise it will return the result.

.. code-block:: python

    @app.route("/user-by-id/<int:id>")
    def user_by_id(id):
        user = db.get_or_404(User, id)
        return render_template("show_user.html", user=user)

    @app.route("/user-by-username/<username>")
    def user_by_username(username):
        user = db.one_or_404(db.select(User).filter_by(username=username))
        return render_template("show_user.html", user=user)

You can add a custom message to the 404 error:

    .. code-block:: python

        user = db.one_or_404(
            db.select(User).filter_by(username=username),
            description=f"No user named '{username}'."
        )


Legacy Query Interface
----------------------

You may see uses of ``Model.query`` or ``session.query`` to build queries. That query
interface is considered legacy in SQLAlchemy. Prefer using the
``session.execute(select(...))`` instead.

See :doc:`legacy-query` for documentation.
