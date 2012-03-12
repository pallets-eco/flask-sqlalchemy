================
Flask-SQLAlchemy
================

Adds SQLAlchemy support to Flask.  Under development.

Quickstart
==========

Install the package::

    pip install Flask-SQLAlchemy

In your Flask app, import the extension and initialize the DB::

    from flaskext.sqlalchemy import SQLAlchemy
    app.config['SQLALCHEMY_ENGINE'] = 'sqlite:////code/apicurious/db.sqlite'
    app.config['SQLALCHEMY_ECHO'] = True
    db = SQLAlchemy(app)

Instead of declaring your models via ``declarative_base()`` as you usually
would with SQLAlchemy, subclass from db.Model::

    class Note(db.Model):
        __tablename__ = "notes"

        id   = db.Column(db.Integer, primary_key=true)
        text = db.Column(db.String(length=255))

        def __init__(self, text):
            self.text = text

To create the database tables, run::

    db.create_all()

If you've set ``app.config['SQLALCHEMY_ECHO'] = True``, you will see the SQL
statments that the database will execute::

    2012-03-12 12:15:07,793 INFO sqlalchemy.engine.base.Engine PRAGMA table_info("notes")
    2012-03-12 12:15:07,793 INFO sqlalchemy.engine.base.Engine ()
    2012-03-12 12:15:07,794 INFO sqlalchemy.engine.base.Engine 
    CREATE TABLE notes (
            id INTEGER NOT NULL, 
            text VARCHAR(255), 
            PRIMARY KEY (id)
    )


    2012-03-12 12:15:07,794 INFO sqlalchemy.engine.base.Engine ()
    2012-03-12 12:15:07,794 INFO sqlalchemy.engine.base.Engine COMMIT

To create a record, use ``db.session.add``. For more information on sessions,
refer to the `SQLAchemy documention on sessions
<http://docs.sqlalchemy.org/en/latest/orm/session.html>`_::

    note = Note('Hello World')
    db.session.add(note)
    db.session.commit()

To query, use ``<Model>.query``::

    >>> print Note.query.get(1).text
    'Hello World'


