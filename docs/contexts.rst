Flask Application Context
=========================

An active Flask application context is required to make queries and to access
``db.engine`` and ``db.session``. This is because the session is scoped to the context
so that it is cleaned up properly after every request or CLI command.

Regardless of how an application is initialized with the extension, it is not stored for
later use. Instead, the extension uses Flask's ``current_app`` proxy to get the active
application, which requires an active application context.


Automatic Context
-----------------

When Flask is handling a request or a CLI command, an application context will
automatically be pushed. Therefore you don't need to do anything special to use the
database during requests or CLI commands.


Manual Context
--------------

If you try to use the database when an application context is not active, you will see
the following error.

.. code-block:: text

    RuntimeError: Working outside of application context.

    This typically means that you attempted to use functionality that needed
    the current application. To solve this, set up an application context
    with app.app_context(). See the documentation for more information.

If you find yourself in a situation where you need the database and don't have a
context, you can push one with ``app_context``. This is common when calling
``db.create_all`` to create the tables, for example.

.. code-block:: python

    def create_app():
        app = Flask(__name__)
        app.config.from_object("project.config")

        import project.models

        with app.app_context():
            db.create_all()

        return app


Tests
-----

If you test your application using the Flask test client to make requests to your
endpoints, the context will be available as part of the request. If you need to test
something about your database or models directly, rather than going through a request,
you need to push a context manually.

Only push a context exactly where and for how long it's needed for each test. Do not
push an application context globally for every test, as that can interfere with how the
session is cleaned up.

.. code-block:: python

    def test_user_model(app):
        user = User()

        with app.app_context():
            db.session.add(user)
            db.session.commit()

If you find yourself writing many tests like that, you can use a pytest fixture to push
a context for a specific test.

.. code-block:: python

    import pytest

    @pytest.mark.fixture
    def app_ctx(app):
        with app.app_context():
            yield

    @pytest.mark.usefixtures("app_ctx")
    def test_user_model(app):
        user = User()
        db.session.add(user)
        db.session.commit()
