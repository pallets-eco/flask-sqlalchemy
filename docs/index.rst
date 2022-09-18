.. rst-class:: hide-header

Flask-SQLAlchemy
================

.. image:: _static/flask-sqlalchemy-title.png
    :align: center

Flask-SQLAlchemy is an extension for `Flask`_ that adds support for `SQLAlchemy`_ to
your application. It simplifies using SQLAlchemy with Flask by setting up common objects
and patterns for using those objects, such as a session tied to each web request, models,
and engines.

Flask-SQLAlchemy does not change how SQLAlchemy works or is used. See the
`SQLAlchemy documentation`_ to learn how to work with the ORM in depth. The
documentation here will only cover setting up the extension, not how to use SQLAlchemy.

.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _Flask: https://flask.palletsprojects.com/
.. _SQLAlchemy documentation: https://docs.sqlalchemy.org/


User Guide
----------

.. toctree::
    :maxdepth: 2

    quickstart
    config
    models
    queries
    pagination
    contexts
    binds
    record-queries
    track-modifications
    customizing


API Reference
-------------

.. toctree::
    :maxdepth: 2

    api


Additional Information
----------------------

.. toctree::
    :maxdepth: 2

    license
    changes
