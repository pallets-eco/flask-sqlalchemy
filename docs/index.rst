.. rst-class:: hide-header

Flask-SQLAlchemy
================

.. image:: _static/flask-sqlalchemy-title.png
    :align: center

Flask-SQLAlchemy is an extension for `Flask`_ that adds support for `SQLAlchemy`_ to your
application.  It aims to simplify using SQLAlchemy with Flask by providing useful defaults and extra
helpers that make it easier to accomplish common tasks.

.. _SQLAlchemy: https://www.sqlalchemy.org/
.. _Flask: http://flask.pocoo.org/

See `the SQLAlchemy documentation`_ to learn how to work with the ORM in depth.  The following
documentation is a brief overview of the most common tasks, as well as the features specific to
Flask-SQLAlchemy.

.. _the SQLAlchemy documentation: https://docs.sqlalchemy.org/en/latest/

Requirements
------------

.. csv-table::
   :header: "Our Version", "Python", "Flask", "SQLAlchemy"

   "2.x", "2.7, 3.4+", 0.12+, "0.8+ or 1.0.10+ w/ Python 3.7"
   "3.0+ (in dev)", "2.7, 3.5+", 1.0+, 1.0+

User Guide
----------

.. toctree::
   :maxdepth: 2

   quickstart
   contexts
   config
   models
   queries
   binds
   signals
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
   changelog
