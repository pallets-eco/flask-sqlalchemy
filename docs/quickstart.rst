.. _quickstart:

Quickstart
==========

.. currentmodule:: flask.ext.sqlalchemy

Flask-SQLAlchemy is fun to use, incredibly easy for basic applications, and
readily extends for larger applications.  For the complete guide, checkout out
the API documentation on the :class:`SQLAlchemy` class.

A Minimal Application
---------------------

For the common case of having one Flask application all you have to do is
to create your Flask application, load the configuration of choice and
then create the :class:`SQLAlchemy` object by passing it the application.

Once created, that object then contains all the functions and helpers
from both :mod:`sqlalchemy` and :mod:`sqlalchemy.orm`.  Furthermore it
provides a class called `Model` that is a declarative base which can be
used to declare models::

    from flask import Flask
    from flask.ext.sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
    db = SQLAlchemy(app)


    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)
        email = db.Column(db.String(120), unique=True)

        def __init__(self, username, email):
            self.username = username
            self.email = email

        def __repr__(self):
            return '<User %r>' % self.username

To create the initial database, just import the `db` object from a
interactive Python shell and run the
:meth:`SQLAlchemy.create_all` method to create the
tables and database:

>>> from yourapplication import db
>>> db.create_all()

Boom, and there is your database.  Now to create some users:

>>> from yourapplication import User
>>> admin = User('admin', 'admin@example.com')
>>> guest = User('guest', 'guest@example.com')

But they are not yet in the database, so let's make sure they are:

>>> db.session.add(admin)
>>> db.session.add(guest)
>>> db.session.commit()

Accessing the data in database is easy as a pie:

>>> users = User.query.all()
[<User u'admin'>, <User u'guest'>]
>>> admin = User.query.filter_by(username='admin').first()
<User u'admin'>

Simple Relationships
--------------------

SQLAlchemy collects to relational databases and what relational databases
are really good at are relations.  As such, we shall have an example of an
application that uses two tables that have a relationship to each other::


    from datetime import datetime


    class Post(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        title = db.Column(db.String(80))
        body = db.Column(db.Text)
        pub_date = db.Column(db.DateTime)

        category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
        category = db.relationship('Category',
            backref=db.backref('posts', lazy='dynamic'))

        def __init__(self, title, body, category, pub_date=None):
            self.title = title
            self.body = body
            if pub_date is None:
                pub_date = datetime.utcnow()
            self.pub_date = pub_date
            self.category = category

        def __repr__(self):
            return '<Post %r>' % self.title


    class Category(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))

        def __init__(self, name):
            self.name = name

        def __repr__(self):
            return '<Category %r>' % self.name

First let's create some objects:

>>> py = Category('Python')
>>> p = Post('Hello Python!', 'Python is pretty cool', py)
>>> db.session.add(py)
>>> db.session.add(p)

Now because we declared `posts` as dynamic relationship in the backref
it shows up as query:

>>> py.posts
<sqlalchemy.orm.dynamic.AppenderBaseQuery object at 0x1027d37d0>

It behaves like a regular query object so we can ask it for all posts that
are associated with our test “Python” category:

>>> py.posts.all()
[<Post 'Hello Python!'>]


Road to Enlightenment
---------------------

The only things you need to know compared to plain SQLAlchemy are:

1.  :class:`SQLAlchemy` gives you access to the following things:

    -   all the functions and classes from :mod:`sqlalchemy` and
        :mod:`sqlalchemy.orm`
    -   a preconfigured scoped session called `session`
    -   the :attr:`~SQLAlchemy.metadata`
    -   the :attr:`~SQLAlchemy.engine`
    -   a :meth:`SQLAlchemy.create_all` and :meth:`SQLAlchemy.drop_all`
        methods to create and drop tables according to the models.
    -   a :class:`Model` baseclass that is a configured declarative base.

2.  The :class:`Model` declarative base class behaves like a regular
    Python class but has a `query` attribute attached that can be used to
    query the model.  (:class:`Model` and :class:`BaseQuery`)

3.  You have to commit the session, but you don't have to remove it at
    the end of the request, Flask-SQLAlchemy does that for you.
