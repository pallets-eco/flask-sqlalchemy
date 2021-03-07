Flaskr
======

The basic blog app built in the Flask `tutorial`_, modified to use
Flask-SQLAlchemy instead of plain SQL.

.. _tutorial: https://flask.palletsprojects.com/tutorial/


Install
-------

**Be sure to use the same version of the code as the version of the docs
you're reading.** You probably want the latest tagged version, but the
default Git version is the master branch.

.. code-block:: text

    # clone the repository
    $ git clone https://github.com/pallets/flask-sqlalchemy
    $ cd flask-sqlalchemy/examples/flaskr
    # checkout the correct version
    $ git checkout correct-version-tag

Create a virtualenv and activate it:

.. code-block:: text

    $ python3 -m venv venv
    $ . venv/bin/activate

Or on Windows cmd:

.. code-block:: text

    $ py -3 -m venv venv
    $ venv\Scripts\activate.bat

Install Flaskr:

.. code-block:: text

    $ pip install -e .

Or if you are using the master branch, install Flask-SQLAlchemy from
source before installing Flaskr:

.. code-block:: text

    $ pip install -e ../..
    $ pip install -e .


Run
---

.. code-block:: text

    $ export FLASK_APP=flaskr
    $ export FLASK_ENV=development
    $ flask init-db
    $ flask run

Or on Windows cmd:

.. code-block:: text

    > set FLASK_APP=flaskr
    > set FLASK_ENV=development
    > flask init-db
    > flask run

Open http://127.0.0.1:5000 in a browser.


Test
----

.. code-block:: text

    $ pip install -e '.[test]'
    $ pytest

Run with coverage report:

.. code-block:: text

    $ coverage run -m pytest
    $ coverage report
    $ coverage html  # open htmlcov/index.html in a browser
