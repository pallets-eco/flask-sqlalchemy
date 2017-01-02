.. _models:

.. currentmodule:: flask_sqlalchemy

Declaring Models
================

Generally Flask-SQLAlchemy behaves like a properly configured declarative
base from the :mod:`~sqlalchemy.ext.declarative` extension.  As such we
recommend reading the SQLAlchemy docs for a full reference.  However the
most common use cases are also documented here.

Things to keep in mind:

-   The baseclass for all your models is called `db.Model`.  It's stored
    on the SQLAlchemy instance you have to create.  See :ref:`quickstart`
    for more details.
-   Some parts that are required in SQLAlchemy are optional in
    Flask-SQLAlchemy.  For instance the table name is automatically set
    for you unless overridden.  It's derived from the class name converted
    to lowercase and with “CamelCase” converted to “camel_case”.  To override
    the table name, set the `__tablename__` class attribute.

Simple Example
--------------

A very simple example::

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(80), unique=True)
        email = db.Column(db.String(120), unique=True)

        def __init__(self, username, email):
            self.username = username
            self.email = email

        def __repr__(self):
            return '<User %r>' % self.username

Use :class:`~sqlalchemy.Column` to define a column.  The name of the
column is the name you assign it to.  If you want to use a different name
in the table you can provide an optional first argument which is a string
with the desired column name.  Primary keys are marked with
``primary_key=True``.  Multiple keys can be marked as primary keys in
which case they become a compound primary key.

The types of the column are the first argument to
:class:`~sqlalchemy.Column`.  You can either provide them directly or call
them to further specify them (like providing a length).  The following
types are the most common:

=================== =====================================
`Integer`           an integer
`String` (size)     a string with a maximum length
`Text`              some longer unicode text
`DateTime`          date and time expressed as Python
                    :mod:`~datetime.datetime` object.
`Float`             stores floating point values
`Boolean`           stores a boolean value
`PickleType`        stores a pickled Python object
`LargeBinary`       stores large arbitrary binary data
=================== =====================================

One-to-Many Relationships
-------------------------

The most common relationships are one-to-many relationships.  Because
relationships are declared before they are established you can use strings
to refer to classes that are not created yet (for instance if `Person`
defines a relationship to `Address` which is declared later in the file).

Relationships are expressed with the :func:`~sqlalchemy.orm.relationship`
function.  However the foreign key has to be separately declared with the
:class:`sqlalchemy.schema.ForeignKey` class::

    class Person(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        addresses = db.relationship('Address', backref='person',
                                    lazy='dynamic')

    class Address(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(50))
        person_id = db.Column(db.Integer, db.ForeignKey('person.id'))

What does ``db.relationship()`` do?  That function returns a new property
that can do multiple things.  In this case we told it to point to the
`Address` class and load multiple of those.  How does it know that this
will return more than one address?  Because SQLAlchemy guesses a useful
default from your declaration.  If you would want to have a one-to-one
relationship you can pass ``uselist=False`` to
:func:`~sqlalchemy.orm.relationship`.

So what do `backref` and `lazy` mean?  `backref` is a simple way to also
declare a new property on the `Address` class.  You can then also use
``my_address.person`` to get to the person at that address.  `lazy` defines
when SQLAlchemy will load the data from the database:

-   ``'select'`` (which is the default) means that SQLAlchemy will load
    the data as necessary in one go using a standard select statement.
-   ``'joined'`` tells SQLAlchemy to load the relationship in the same
    query as the parent using a `JOIN` statement.
-   ``'subquery'`` works like ``'joined'`` but instead SQLAlchemy will
    use a subquery.
-   ``'dynamic'`` is special and useful if you have many items.  Instead of
    loading the items SQLAlchemy will return another query object which
    you can further refine before loading the items.  This is usually
    what you want if you expect more than a handful of items for this
    relationship.

How do you define the lazy status for backrefs?  By using the
:func:`~sqlalchemy.orm.backref` function::

    class User(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        addresses = db.relationship('Address',
            backref=db.backref('person', lazy='joined'), lazy='dynamic')

Many-to-Many Relationships
--------------------------

If you want to use many-to-many relationships you will need to define a
helper table that is used for the relationship.  For this helper table it
is strongly recommended to *not* use a model but an actual table::

    tags = db.Table('tags',
        db.Column('tag_id', db.Integer, db.ForeignKey('tag.id')),
        db.Column('page_id', db.Integer, db.ForeignKey('page.id'))
    )

    class Page(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        tags = db.relationship('Tag', secondary=tags,
            backref=db.backref('pages', lazy='dynamic'))

    class Tag(db.Model):
        id = db.Column(db.Integer, primary_key=True)

Here we configured `Page.tags` to be a list of tags once loaded because we
don't expect too many tags per page.  The list of pages per tag
(`Tag.pages`) however is a dynamic backref.  As mentioned above this means
that you will get a query object back you can use to fire a select yourself.


External Declarative Bases
--------------------------

Flask-SQLAlchemy allows you to provide your own declarative base if you 
feel the need to do so. Doing so can allow you to cut down circular 
imports, allow you to use the app factory pattern, or even share your 
SQLAlchemy model across different python application using SQLAlchemy, 
without the requirement of running a different set of models for use with
Flask-SQLAlchemy.

We declare our model just as you would above, however, using SQLAlchemy 
constructs, rather than accessing classes via ``db.*``. Once defined, call 
call :meth:`SQLAlchemy.register_base` to register your delcarative base with 
Flask-SQLAlchemy.

A minimal example::

    from sqlalchemy import Column, Integer, String
    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    class User(Base):
        __tablename__ = 'user'

        id = Column(Integer, primary_key=True)
        username = Column(String(80), unique=True)
        email = Column(String(255), unique=True)

        def __repr__(self):
            return '<User %r>' % self.username

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
    db = SQLAlchemy(app)
    db.register_base(Base)

    db.create_all()

    @app.before_first_request
    def insert_user():
        # We can create new objects the normal way
        user = User(id=1, username='foo', email='foo@bar.com')
        db.session.add(user)
        db.session.commit()

    @app.route('/<int:user_id>')
    def index(user_id):
        # We can query the model two ways:
        user = db.session.query(User).get_or_404(user_id)

        # Or we can using the model's query property
        user = User.query.get_or_404(user_id)

        return "Hello, {}".format(user.username)

    if __name__ == '__main__':
        app.run(debug=True)

If you're using binds, you'll need to use your own session that knows how 
to handle them, or use the same ``Model.__bind__`` system and register the 
extra engines with ``SQLALCHEMY_BINDS``

