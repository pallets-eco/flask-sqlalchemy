:orphan:

Legacy Query Interface
======================

.. warning::
    The query interface is considered legacy in SQLAlchemy. Prefer using
    ``session.execute(select(...))`` instead.

Flask-SQLAlchemy adds a ``query`` object to each model. This can be used to query
instances of a given model. ``User.query`` is a shortcut for ``db.session.query(User)``.

.. code-block:: python

    # get the user with id 5
    user = User.query.get(5)

    # get a user by username
    user = User.query.filter_by(username=username).one()


Queries for Views
-----------------

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


Pagination
----------

If you have a lot of results, you may only want to show a certain number at a time,
allowing the user to click next and previous links to see pages of data.

Call :meth:`~.Query.paginate` on a query to get a :class:`.Pagination` object. See
:doc:`/pagination` for more information about the pagination object.

During a request, this will take ``page`` and ``per_page`` arguments from the query
string ``request.args``. Pass ``max_per_page`` to prevent users from requesting too many
results on a single page. If not given, the default values will be page 1 with 20 items
per page.

.. code-block:: python

    page = User.query.order_by(User.join_date).paginate()
    return render_template("user/list.html", page=page)
