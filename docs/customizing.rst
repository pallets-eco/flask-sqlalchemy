.. _customizing:

.. currentmodule:: flask_sqlalchemy

Customizing
===========

Flask-SQLAlchemy defines sensible defaults. However, sometimes customization is
needed. Two major pieces to customize are the Model base class and the default
Query class.

Both of these customizations are applied at the creation of the :class:`SQLAlchemy`
object and extend to all models derived from its ``Model`` class.

Model Class
-----------

Flask-SQLAlchemy allows defining a custom declarative base, just like SQLAlchemy,
that all model classes should extend from. For example, if all models should have
a custom ``__repr__`` method::

    from flask_sqlalchemy import Model  # this is the default declarative base
    from flask_sqlalchemy import SQLAlchemy

    class ReprBase(Model):
         def __repr__(self):
             return "<{0} id: {1}>".format(self.__class__.__name__, self.id)

    db = SQLAlchemy(model_class=ReprBase)

    class MyModel(db.Model):
        ...

.. note::

        While not strictly necessary to inherit from :class:`flask_sqlalchemy.Model`
        it is encouraged as future changes may cause incompatibility.

.. note::

        If behavior is needed in only some models, not all, a better strategy
        is to use a Mixin, as exampled below.

While this particular example is more useful for debugging, it is possible to
provide many augmentations to models that would otherwise be achieved with
mixins instead. The above example is equivalent to the following::

    class ReprBase(object):
        def __repr__(self):
            return "<{0} id: {1}>".format(self.__class__.__name__, self.id)

    db = SQLAlchemy()

    class MyModel(db.Model, ReprBase):
        ...

It also possible to provide default columns and properties to all models as well::

    from flask_sqlalchemy import Model, SQLAlchemy
    from sqlalchemy import Column, DateTime
    from datetime import datetime

    class TimestampedModel(Model):
        created_at = Column(DateTime, default=datetime.utcnow)

    db = SQLAlchemy(model_class=TimestampedModel)

    class MyModel(db.Model):
        ...

All model classes extending from ``db.Model`` will now inherit a
``created_at`` column.

Query Class
-----------

It is also possible to customize what is availble for use on the
special ``query`` property of models. For example, providing a
``get_or`` method::

    from flask_sqlalchemy import BaseQuery, SQLAlchemy

    class GetOrQuery(BaseQuery):
        def get_or(self, ident, default=None):
            return self.get(ident) or default

    db = SQLAlchemy(query_class=GetOrQuery)

And now all queries executed from the special ``query`` property
on Flask-SQLAlchemy models can use the ``get_or`` method as part
of their queries. All relationships defined with
``db.relationship`` (but not :func:`sqlalchemy.relationship`)
will also be provided with this functionality.

.. warning::

        Unlike a custom ``Model`` base class, it is required
        to either inherit from either :class:`flask_sqlalchemy.BaseQuery`
        or :func:`sqlalchemy.orm.Query` in order to define a custom
        query class.

It also possible to define a custom query class for individual
relationships as well, by providing the ``query_class`` keyword
in the definition. This works with both ``db.relationship``
and ``sqlalchemy.relationship``::

    class MyModel(db.Model):
        cousin = db.relationship('OtherModel', query_class=GetOrQuery)

.. note::

        If a query class is defined on a relationship, it will take
        precedence over the query class attached to its corresponding
        model.

It is also possible to define a specific query class for individual models
by overriding the ``query_class`` class attribute on the model::

    class MyModel(db.Model):
        query_class = GetOrQuery

In this case, the ``get_or`` method will be only availble on queries
orginating from ``MyModel.query``.
