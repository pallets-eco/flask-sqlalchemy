.. _customizing:

.. currentmodule:: flask_sqlalchemy

Customizing
===========

Flask-SQLAlchemy defines sensible defaults. However, sometimes customization is
needed. There are various ways to customize how the models are defined and
interacted with.

These customizations are applied at the creation of the :class:`SQLAlchemy`
object and extend to all models derived from its ``Model`` class.


Model Class
-----------

SQLAlchemy models all inherit from a declarative base class. This is exposed
as ``db.Model`` in Flask-SQLAlchemy, which all models extend. This can be
customized by subclassing the default and passing the custom class to
``model_class``.

The following example gives every model an integer primary key, or a foreign
key for joined-table inheritance.

.. note::

    Integer primary keys for everything is not necessarily the best database
    design (that's up to your project's requirements), this is only an example.

::

    from flask_sqlalchemy import Model, SQLAlchemy
    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declared_attr, has_inherited_table

    class IdModel(Model):
        @declared_attr
        def id(cls):
            for base in cls.__mro__[1:-1]:
                if getattr(base, '__table__', None) is not None:
                    type = sa.ForeignKey(base.id)
                    break
            else:
                type = sa.Integer

            return sa.Column(type, primary_key=True)

    db = SQLAlchemy(model_class=IdModel)

    class User(db.Model):
        name = db.Column(db.String)

    class Employee(User):
        title = db.Column(db.String)


Model Mixins
------------

If behavior is only needed on some models rather than all models, use mixin
classes to customize only those models. For example, if some models should
track when they are created or updated::

    from datetime import datetime

    class TimestampMixin(object):
        created = db.Column(
            db.DateTime, nullable=False, default=datetime.utcnow)
        updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    class Author(db.Model):
        ...

    class Post(TimestampMixin, db.Model):
        ...


Query Class
-----------

It is also possible to customize what is available for use on the
special ``query`` property of models. For example, providing a
``get_or`` method::

    from flask_sqlalchemy import BaseQuery, SQLAlchemy

    class GetOrQuery(BaseQuery):
        def get_or(self, ident, default=None):
            return self.get(ident) or default

    db = SQLAlchemy(query_class=GetOrQuery)

    # get a user by id, or return an anonymous user instance
    user = User.query.get_or(user_id, anonymous_user)

And now all queries executed from the special ``query`` property
on Flask-SQLAlchemy models can use the ``get_or`` method as part
of their queries. All relationships defined with
``db.relationship`` (but not :func:`sqlalchemy.orm.relationship`)
will also be provided with this functionality.

It also possible to define a custom query class for individual
relationships as well, by providing the ``query_class`` keyword
in the definition. This works with both ``db.relationship``
and ``sqlalchemy.relationship``::

    class MyModel(db.Model):
        cousin = db.relationship('OtherModel', query_class=GetOrQuery)

.. note::

    If a query class is defined on a relationship, it will take precedence over
    the query class attached to its corresponding model.

It is also possible to define a specific query class for individual models
by overriding the ``query_class`` class attribute on the model::

    class MyModel(db.Model):
        query_class = GetOrQuery

In this case, the ``get_or`` method will be only availble on queries
orginating from ``MyModel.query``.


Model Metaclass
---------------

.. warning::

    Metaclasses are an advanced topic, and you probably don't need to customize
    them to achieve what you want. It is mainly documented here to show how to
    disable table name generation.

The model metaclass is responsible for setting up the SQLAlchemy internals when
defining model subclasses. Flask-SQLAlchemy adds some extra behaviors through
mixins; its default metaclass, :class:`~model.DefaultMeta`, inherits them all.

* :class:`~model.BindMetaMixin`: ``__bind_key__`` is extracted from the class
  and applied to the table. See :ref:`binds`.
* :class:`~model.NameMetaMixin`: If the model does not specify a
  ``__tablename__`` but does specify a primary key, a name is automatically
  generated.

You can add your own behaviors by defining your own metaclass and creating the
declarative base yourself. Be sure to still inherit from the mixins you want
(or just inherit from the default metaclass).

Passing a declarative base class instead of a simple model base class, as shown
above, to ``base_class`` will cause Flask-SQLAlchemy to use this base instead
of constructing one with the default metaclass. ::

    from flask_sqlalchemy import SQLAlchemy
    from flask_sqlalchemy.model import DefaultMeta, Model

    class CustomMeta(DefaultMeta):
        def __init__(cls, name, bases, d):
            # custom class setup could go here

            # be sure to call super
            super(CustomMeta, cls).__init__(name, bases, d)

        # custom class-only methods could go here

    db = SQLAlchemy(model_class=declarative_base(
        cls=Model, metaclass=CustomMeta, name='Model'))

You can also pass whatever other arguments you want to
:func:`~sqlalchemy.ext.declarative.declarative_base` to customize the base
class as needed.

Disabling Table Name Generation
```````````````````````````````

Some projects prefer to set each model's ``__tablename__`` manually rather than
relying on Flask-SQLAlchemy's detection and generation. The table name
generation can be disabled by defining a custom metaclass. ::

    from flask_sqlalchemy.model import BindMetaMixin, Model
    from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base

    class NoNameMeta(BindMetaMixin, DeclarativeMeta):
        pass

    db = SQLAlchemy(model_class=declarative_base(
        cls=Model, metaclass=NoNameMeta, name='Model'))

This creates a base that still supports the ``__bind_key__`` feature but does
not generate table names.
