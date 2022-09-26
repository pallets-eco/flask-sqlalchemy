Advanced Customization
======================

The various objects managed by the extension can be customized by passing arguments to
the :class:`.SQLAlchemy` constructor.


Model Class
-----------

SQLAlchemy models all inherit from a declarative base class. This is exposed as
``db.Model`` in Flask-SQLAlchemy, which all models extend. This can be customized by
subclassing the default and passing the custom class to ``model_class``.

The following example gives every model an integer primary key, or a foreign key for
joined-table inheritance.

.. note::
    Integer primary keys for everything is not necessarily the best database design
    (that's up to your project's requirements), this is only an example.

.. code-block:: python

    from flask_sqlalchemy.model import model
    import sqlalchemy as sa
    import sqlalchemy.orm

    class IdModel(Model):
        @sa.orm.declared_attr
        def id(cls):
            for base in cls.__mro__[1:-1]:
                if getattr(base, "__table__", None) is not None:
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


Abstract Models and Mixins
--------------------------

If behavior is only needed on some models rather than all models, use an abstract model
base class to customize only those models. For example, if some models should track when
they are created or updated.

.. code-block:: python

    from datetime import datetime

    class TimestampModel(db.Model):
        __abstract__ = True
        created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    class Author(db.Model):
        ...

    class Post(TimestampModel):
        ...

This can also be done with a mixin class, inheriting from ``db.Model`` separately.

.. code-block:: python

    class TimestampMixin:
        created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
        updated = db.Column(db.DateTime, onupdate=datetime.utcnow)

    class Post(TimestampMixin, db.Model):
        ...


Session Class
-------------

Flask-SQLAlchemy's :class:`.Session` class chooses which engine to query based on the
bind key associated with the model or table. However, there are other strategies such as
horizontal sharding that can be implemented with a different session class. The
``class_`` key to the ``session_options`` argument to the extension to change the
session class.

Flask-SQLAlchemy will always pass the extension instance as the ``db`` argument to the
session, so it must accept that to continue working. That can be used to get access to
``db.engines``.

.. code-block:: python

    from sqlalchemy.ext.horizontal_shard import ShardedSession
    from flask_sqlalchemy.session import Session

    class CustomSession(ShardedSession, Session):
        ...

    db = SQLAlchemy(session_options={"class_": CustomSession})


Query Class
-----------

.. warning::
    The query interface is considered legacy in SQLAlchemy. This includes
    ``session.query``, ``Model.query``, ``db.Query``, and ``lazy="dynamic"``
    relationships. Prefer using ``session.execute(select(...))`` instead.

It is possible to customize the query interface used by the session, models, and
relationships. This can be used to add extra query methods. For example, you could add
a ``get_or`` method that gets a row or returns a default.

.. code-block:: python

    from flask_sqlalchemy.query import Query

    class GetOrQuery(Query):
        def get_or(self, ident, default=None):
            out = self.get(ident)

            if out is None:
                return default

            return out

    db = SQLAlchemy(query_class=GetOrQuery)

    user = User.query.get_or(user_id, anonymous_user)

Passing the ``query_class`` argument will customize ``db.Query``, ``db.session.query``,
``Model.query``, and ``db.relationship(lazy="dynamic")`` relationships. It's also
possible to customize these on a per-object basis.

To customize a specific model's ``query`` property, set the ``query_class`` attribute on
the model class.

.. code-block:: python

    class User(db.Model):
        query_class = GetOrQuery

To customize a specific dynamic relationship, pass the ``query_class`` argument to the
relationship.

.. code-block:: python

    db.relationship(User, lazy="dynamic", query_class=GetOrQuery)

To customize only ``session.query``, pass the ``query_cls`` key to the
``session_options`` argument to the constructor.

.. code-block:: python

    db = SQLAlchemy(session_options={"query_cls": GetOrQuery})


Model Metaclass
---------------

.. warning::
    Metaclasses are an advanced topic, and you probably don't need to customize them to
    achieve what you want. It is mainly documented here to show how to disable table
    name generation.

The model metaclass is responsible for setting up the SQLAlchemy internals when defining
model subclasses. Flask-SQLAlchemy adds some extra behaviors through mixins; its default
metaclass, :class:`~.DefaultMeta`, inherits them all.

-   :class:`.BindMetaMixin`: ``__bind_key__`` sets the bind to use for the model.
-   :class:`.NameMetaMixin`: If the model does not specify a ``__tablename__`` but does
    specify a primary key, a name is automatically generated.

You can add your own behaviors by defining your own metaclass and creating the
declarative base yourself. Be sure to still inherit from the mixins you want (or just
inherit from the default metaclass).

Passing a declarative base class instead of a simple model base class to ``model_class``
will cause Flask-SQLAlchemy to use this base instead of constructing one with the
default metaclass.

.. code-block:: python

    from sqlalchemy.orm import declarative_base
    from flask_sqlalchemy import SQLAlchemy
    from flask_sqlalchemy.model import DefaultMeta, Model

    class CustomMeta(DefaultMeta):
        def __init__(cls, name, bases, d):
            # custom class setup could go here

            # be sure to call super
            super(CustomMeta, cls).__init__(name, bases, d)

        # custom class-only methods could go here

    CustomModel = declarative_base(cls=Model, metaclass=CustomMeta, name="Model")
    db = SQLAlchemy(model_class=CustomModel)

You can also pass whatever other arguments you want to
:func:`~sqlalchemy.orm.declarative_base` to customize the base class.


Disabling Table Name Generation
```````````````````````````````

Some projects prefer to set each model's ``__tablename__`` manually rather than relying
on Flask-SQLAlchemy's detection and generation. The simple way to achieve that is to
set each ``__tablename__`` and not modify the base class. However, the table name
generation can be disabled by defining a custom metaclass with only the
``BindMetaMixin`` and not the ``NameMetaMixin``.

.. code-block:: python

    from sqlalchemy.orm import DeclarativeMeta, declarative_base
    from flask_sqlalchemy.model import BindMetaMixin, Model

    class NoNameMeta(BindMetaMixin, DeclarativeMeta):
        pass

    CustomModel = declarative_base(cls=Model, metaclass=NoNameMeta, name="Model")
    db = SQLAlchemy(model_class=CustomModel)

This creates a base that still supports the ``__bind_key__`` feature but does not
generate table names.
