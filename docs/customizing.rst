.. _customizing:

.. currentmodule:: flask_sqlalchemy

Customizing
===========

Flask-SQLAlchemy defines sensible defaults. However, sometimes customization is
needed. The two major points to add customization is with the Model base class
and the default Query class. Both of these are defined at the creation of the
:class:`SQLAlchemy` object.

Model Class
-----------

Flask-SQLAlchemy allows defining a custom declarative base, just like SQLAlchemy,
that you can define your model classes to extend from. For example, if you wanted
all of your models to share a custom ``__repr__`` method, you could do::


    from flask_sqlalchemy import Model  # this is the default declarative base
    from flask_sqlalchemy import SQLAlchemy

    class ReprBase(Model):
         def __repr__(self):
             return "<{0} id: {1}>".format(self.__class__.__name__, self.id)

    db = SQLAlchemy(model_class=ReprBase)

    class MyModel(db.Model):
        ...

And all class inherited from ``db.Model`` will have the customized ``__repr__``
method. This is just like passing a custom class to
:func:`sqlalchemy.ext.declarative.declarative_base`.

.. note::

        While not strictly necessary to inherit from :class:`flask_sqlalchemy.Model`
        it is encouraged as future changes may cause incompatibility if you do not.

.. note::

        If behavior is needed in only *some* models, not all, a better strategy
        is to use a Mixin, as exampled below.

While this particular example is more useful for debugging, it is possible to
provide all manner of augmentations to your models that would otherwise be
achieved with mixins instead. The above example is equivalent to the following::

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

All model classes extending from ``db.Model`` will now also inherit a
``created_at`` attribute as well.

Query Class
----------

It is also possible to customize what is availble for use on the
special ``query`` property of models. For example, providing a
``get_or`` method::

    from flask_sqlalchemy import BaseQuery, SQLAlchemy

    class GetOrQuery(BaseQuery):
        def get_or(self, ident, default=None):
            return self.get(ident) or default

    db = SQLAlchemy(query_class=GetOrQuery)

And now all queries from ``db.Model`` derived classes can use
``get_or`` as part of their queries. All relationships defined with
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
