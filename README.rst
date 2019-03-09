Flask-SQLAlchemy
################

Flask-SQLAlchemy is a Flask_ extension which adds support for the SQLAlchemy_ ORM/toolkit.


Installing
==========

Install and update using `pip`_:

.. code-block:: text

  $ pip install -U flask-sqlalchemy

We encourage you to use a virtualenv_. Check the docs for complete installation, version
requirement, and usage instructions.


A Simple Example
================

Pretty easy to get started:

.. code-block:: python

  from flask import Flask
  from flask_sqlalchemy import SQLAlchemy

  app = Flask(__name__)
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
  db = SQLAlchemy(app)


  class User(db.Model):
      id = db.Column(db.Integer, primary_key=True)
      username = db.Column(db.String(80), unique=True, nullable=False)
      email = db.Column(db.String(120), unique=True, nullable=False)

For more details, see the `quickstart example
<http://flask-sqlalchemy.pocoo.org/latest/quickstart/#a-minimal-application>`_.


Tests
=====

In short we use pytest_ and tox_.  You should be able to::

  $ git clone git@github.com:pallets/flask-sqlalchemy.git
  $ cd flask-sqlalchemy
  $ tox

That will run everything, so you  might want to start with something like `tox -e py37` or whatever
version of Python you have installed.

You can figure out our testing and documentation dependencies by further inspecting the `tox.ini`
file in the root of the project.

Help
====

- Join us on the #pocoo IRC channel on irc.freenode.net.
- Join us at: https://discord.gg/t6rrQZH


Links
=====

-   Home: https://github.com/pallets/flask-sqlalchemy
-   Documentation: http://flask-sqlalchemy.pocoo.org/
-   Releases: https://pypi.org/project/Flask-SQLAlchemy/
-   Issue tracker: https://github.com/pallets/flask-sqlalchemy/issues
-   Test status:

    -   Linux, Mac: https://travis-ci.org/pallets/flask-sqlalchemy/
    -   Windows: None yet, see `#690 <https://github.com/pallets/flask-sqlalchemy/issues/690>`_

-   Test coverage: https://codecov.io/gh/pallets/flask-sqlalchemy/


.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _Flask: https://www.palletsprojects.com/p/flask/
.. _pip: https://pip.pypa.io/en/stable/quickstart/
.. _pytest: https://docs.pytest.org/en/latest/
.. _tox: https://tox.readthedocs.io/en/latest/
.. _virtualenv: https://packaging.python.org/guides/installing-using-pip-and-virtualenv/
