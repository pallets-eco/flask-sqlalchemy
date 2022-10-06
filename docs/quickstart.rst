.. _quickstart:

Quick Start
===========

.. currentmodule:: flask_sqlalchemy

Flask-SQLAlchemy simplifies using SQLAlchemy by automatically handling creating, using,
and cleaning up the SQLAlchemy objects you'd normally work with. While it adds a few
useful features, it still works like SQLAlchemy.

This page will walk you through the basic use of Flask-SQLAlchemy. For full capabilities
and customization, see the rest of these docs, including the API docs for the
:class:`SQLAlchemy` object.


Check the SQLAlchemy Documentation
----------------------------------

Flask-SQLAlchemy is a wrapper around SQLAlchemy. You should follow the
`SQLAlchemy Tutorial`_ to learn about how to use it, and consult its documentation
for detailed information about its features. These docs show how to set up
Flask-SQLAlchemy itself, not how to use SQLAlchemy. Flask-SQLAlchemy sets up the
engine, declarative model class, and scoped session automatically, so you can skip those
parts of the SQLAlchemy tutorial.

.. _SQLAlchemy Tutorial: https://docs.sqlalchemy.org/tutorial/index.html


Installation
------------

Flask-SQLAlchemy is available on `PyPI`_ and can be installed with various Python tools.
For example, to install or update the latest version using pip:

.. code-block:: text

    $ pip install -U Flask-SQLAlchemy

.. _PyPI: https://pypi.org/project/Flask-SQLAlchemy/


Configure the Extension
-----------------------

The only required Flask app config is the :data:`.SQLALCHEMY_DATABASE_URI` key. That
is a connection string that tells SQLAlchemy what database to connect to.

Create your Flask application object, load any config, and then initialize the
:class:`SQLAlchemy` extension class with the application by calling
:meth:`db.init_app <.SQLAlchemy.init_app>`. This example connects to a SQLite database,
which is stored in the app's instance folder.

.. code-block:: python

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    # create the extension
    db = SQLAlchemy()
    # create the app
    app = Flask(__name__)
    # configure the SQLite database, relative to the app instance folder
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
    # initialize the app with the extension
    db.init_app(app)

The ``db`` object gives you access to the :attr:`db.Model <.SQLAlchemy.Model>` class to
define models, and the :attr:`db.session <.SQLAlchemy.session>` to execute queries.

See :doc:`config` for an explanation of connections strings and what other configuration
keys are used. The :class:`SQLAlchemy` object also takes some arguments to customize the
objects it manages.


Define Models
-------------

Subclass ``db.Model`` to define a model class. The ``db`` object makes the names in
``sqlalchemy`` and ``sqlalchemy.orm`` available for convenience, such as ``db.Column``.
The model will generate a table name by converting the ``CamelCase`` class name to
``snake_case``.

.. code-block:: python

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, unique=True, nullable=False)
        email = db.Column(db.String)

The table name ``"user"`` will automatically be assigned to the model's table.

See :doc:`models` for more information about defining and creating models and tables.


Create the Tables
-----------------

After all models and tables are defined, call :meth:`.SQLAlchemy.create_all` to create
the table schema in the database. This requires an application context. Since you're not
in a request at this point, create one manually.

.. code-block:: python

    with app.app_context():
        db.create_all()

If you define models in other modules, you must import them before calling
``create_all``, otherwise SQLAlchemy will not know about them.

``create_all`` does not update tables if they are already in the database. If you change
a model's columns, use a migration library like `Alembic`_ with `Flask-Alembic`_ or
`Flask-Migrate`_ to generate migrations that update the database schema.

.. _Alembic: https://alembic.sqlalchemy.org/
.. _Flask-Alembic: https://flask-alembic.readthedocs.io/
.. _Flask-Migrate: https://flask-migrate.readthedocs.io/


Query the Data
--------------

Within a Flask view or CLI command, you can use ``db.session`` to execute queries and
modify model data.

SQLAlchemy automatically defines an ``__init__`` method for each model that assigns any
keyword arguments to corresponding database columns and other attributes.

``db.session.add(obj)`` adds an object to the session, to be inserted. Modifying an
object's attributes updates the object. ``db.session.delete(obj)`` deletes an object.
Remember to call ``db.session.commit()`` after modifying, adding, or deleting any data.

``db.session.execute(db.select(...))`` constructs a query to select data from the
database. Building queries is the main feature of SQLAlchemy, so you'll want to read its
`tutorial on select`_ to learn all about it. You'll usually use the ``Result.scalars()``
method to get a list of results, or the ``Result.scalar()`` method to get a single
result.

.. _tutorial on select: https://docs.sqlalchemy.org/tutorial/data_select.html

.. code-block:: python

    @app.route("/users")
    def user_list():
        users = db.session.execute(db.select(User).order_by(User.username)).scalars()
        return render_template("user/list.html", users=users)

    @app.route("/users/create", methods=["GET", "POST"])
    def user_create():
        if request.method == "POST":
            user = User(
                username=request.form["username"],
                email=request.form["email"],
            )
            db.session.add(user)
            db.session.commit()
            return redirect(url_for("user_detail", id=user.id))

        return render_template("user/create.html")

    @app.route("/user/<int:id>")
    def user_detail(id):
        user = db.get_or_404(User, id)
        return render_template("user/detail.html", user=user)

    @app.route("/user/<int:id>/delete", methods=["GET", "POST"])
    def user_delete(id):
        user = db.get_or_404(User, id)

        if request.method == "POST":
            db.session.delete(user)
            db.session.commit()
            return redirect(url_for("user_list"))

        return render_template("user/delete.html", user=user)

You may see uses of ``Model.query`` to build queries. This is an older interface for
queries that is considered legacy in SQLAlchemy. Prefer using
``db.session.execute(db.select(...))`` instead.

See :doc:`queries` for more information about queries.


What to Remember
----------------

For the most part, you should use SQLAlchemy as usual. The :class:`SQLAlchemy` extension
instance creates, configures, and gives access to the following things:

-   :attr:`.SQLAlchemy.Model` declarative model base class. It sets the table
    name automatically instead of needing ``__tablename__``.
-   :attr:`.SQLAlchemy.session` is a session that is scoped to the current
    Flask application context. It is cleaned up after every request.
-   :attr:`.SQLAlchemy.metadata` and :attr:`.SQLAlchemy.metadatas` gives access to each
    metadata defined in the config.
-   :attr:`.SQLAlchemy.engine` and :attr:`.SQLAlchemy.engines` gives access to each
    engine defined in the config.
-   :meth:`.SQLAlchemy.create_all` creates all tables.
-   You must be in an active Flask application context to execute queries and to access
    the session and engine.
