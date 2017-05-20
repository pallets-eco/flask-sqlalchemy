
# Flask-SQLAlchemy


## What is Flask-SQLAlchemy?

*  Flask-SQLAlchemy is a Flask microframework extension which adds support for the SQLAlchemy SQL toolkit/ORM.

## What's the latest version?

*  2.1 is the most recent stable version.

## What do I need?

*  SQLAlchemy, and Flask 0.10 or later. `pip` or `easy_install` will install them for you if you do `pip install Flask-SQLAlchemy`.
*  We encourage you to use a virtualenv. Check the docs for complete installation and usage instructions.

## Where are the docs?

*  Go to http://flask-sqlalchemy.pocoo.org/ for a prebuilt version of the current documentation.  Otherwise build them yourself from the sphinx sources in the docs folder.

## Where are the tests?

*  Good that you're asking. To run the tests use the `test_sqlalchemy.py` file:

    ```
    $ python test_sqlalchemy.py
    ```

*  If you just want one particular testcase to run you can provide it on the command line:

    ```
    $ python test_sqlalchemy.py PaginationTestCase
    ```

*  In case you have `tox` installed, you can also run that to have virtualenvs created automatically and tests run inside of them at your convenience. Running just `tox` is enough:

    ```
    $ tox
    ```

## Where can I get help?

*  Join us on the #pocoo IRC channel on irc.freenode.net.
