Flask-SQLAlchemy
================

Flask-SQLAlchemy is an extension for `Flask`_ that adds support for
`SQLAlchemy`_ to your application. It aims to simplify using SQLAlchemy
with Flask by providing useful defaults and extra helpers that make it
easier to accomplish common tasks.

.. _Flask: https://palletsprojects.com/p/flask/
.. _SQLAlchemy: https://www.sqlalchemy.org


Installing
----------

Install and update using `pip`_:

.. code-block:: text

  $ pip install -U Flask-SQLAlchemy

.. _pip: https://pip.pypa.io/en/stable/quickstart/


A Simple Example
----------------

.. code-block:: python

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"
    db = SQLAlchemy(app)


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String, unique=True, nullable=False)
        email = db.Column(db.String, unique=True, nullable=False)


    db.session.add(User(username="Flask", email="example@example.com"))
    db.session.commit()

    users = User.query.all()


Contributing
------------

For guidance on setting up a development environment and how to make a
contribution to Flask-SQLAlchemy, see the `contributing guidelines`_.

.. _contributing guidelines: https://github.com/pallets/flask-sqlalchemy/blob/master/CONTRIBUTING.rst


Donate
------

The Pallets organization develops and supports Flask-SQLAlchemy. In
order to grow the community of contributors and users, and allow the
maintainers to devote more time to the projects, `please donate today`_.

.. _please donate today: https://palletsprojects.com/donate


Links
-----

-   Documentation: https://flask-sqlalchemy.palletsprojects.com/
-   Releases: https://pypi.org/project/Flask-SQLAlchemy/
-   Code: https://github.com/pallets/flask-sqlalchemy
-   Issue tracker: https://github.com/pallets/flask-sqlalchemy/issues
-   Official chat: https://discord.gg/t6rrQZH
