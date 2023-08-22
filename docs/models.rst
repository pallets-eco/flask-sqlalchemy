Models and Tables
=================

Use the ``db.Model`` class to define models, or the ``db.Table`` class to create tables.
Both handle Flask-SQLAlchemy's bind keys to associate with a specific engine.

Initializing the Base Class
---------------------------

``SQLAlchemy`` 2.x offers several possible base classes for your models:
`DeclarativeBase`_ or `DeclarativeBaseNoMeta`_.

Create a subclass of one of those classes:

.. code-block:: python

    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
      pass

.. _DeclarativeBase: https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.DeclarativeBase
.. _DeclarativeBaseNoMeta: https://docs.sqlalchemy.org/en/20/orm/mapping_api.html#sqlalchemy.orm.DeclarativeBaseNoMeta

If desired, you can enable `SQLAlchemy's native support for data classes`_
by adding `MappedAsDataclass` as an additional parent class.

.. code-block:: python

    from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass

    class Base(DeclarativeBase, MappedAsDataclass):
      pass

.. _SQLAlchemy's native support for data classes: https://docs.sqlalchemy.org/en/20/changelog/whatsnew_20.html#native-support-for-dataclasses-mapped-as-orm-models


You can optionally construct the :class:`.SQLAlchemy` object with a custom
:class:`~sqlalchemy.schema.MetaData` object. This allows you to specify a custom
constraint `naming convention`_. This makes constraint names consistent and predictable,
useful when using migrations, as described by `Alembic`_.

.. code-block:: python

    from sqlalchemy import MetaData

    class Base(DeclarativeBase):
        metadata = MetaData(naming_convention={
            "ix": 'ix_%(column_0_label)s',
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        })

.. _naming convention: https://docs.sqlalchemy.org/core/constraints.html#constraint-naming-conventions
.. _Alembic: https://alembic.sqlalchemy.org/en/latest/naming.html


Initialize the Extension
------------------------

Once you've defined a base class, create the ``db`` object using the ``SQLAlchemy`` constructor.

.. code-block:: python

    db = SQLAlchemy(model_class=Base)


Defining Models
---------------

See SQLAlchemy's `declarative documentation`_ for full information about defining model
classes declaratively.

.. _declarative documentation: https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html

Subclass ``db.Model`` to create a model class. Unlike plain SQLAlchemy,
Flask-SQLAlchemy's model will automatically generate a table name if ``__tablename__``
is not set and a primary key column is defined.

.. code-block:: python

    from sqlalchemy.orm import Mapped, mapped_column

    class User(db.Model):
        id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
        username: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)
        email: Mapped[str] = mapped_column(db.String)


Defining a model does not create it in the database. Use :meth:`~.SQLAlchemy.create_all`
to create the models and tables after defining them. If you define models in submodules,
you must import them so that SQLAlchemy knows about them before calling ``create_all``.

.. code-block:: python

    with app.app_context():
        db.create_all()


Defining Tables
---------------

See SQLAlchemy's `table documentation`_ for full information about defining table
objects.

.. _table documentation: https://docs.sqlalchemy.org/en/20/core/metadata.html

Create instances of ``db.Table`` to define tables. The class takes a table name, then
any columns and other table parts such as columns and constraints. Unlike plain
SQLAlchemy, the ``metadata`` argument is not required. A metadata will be chosen based
on the ``bind_key`` argument, or the default will be used.

A common reason to create a table directly is when defining many to many relationships.
The association table doesn't need its own model class, as it will be accessed through
the relevant relationship attributes on the related models.

.. code-block:: python

    import sqlalchemy as sa

    user_book_m2m = db.Table(
        "user_book",
        sa.Column("user_id", sa.ForeignKey(User.id), primary_key=True),
        sa.Column("book_id", sa.ForeignKey(Book.id), primary_key=True),
    )


Reflecting Tables
-----------------

If you are connecting to a database that already has tables, SQLAlchemy can detect that
schema and create tables with columns automatically. This is called reflection. Those
tables can also be assigned to model classes with the ``__table__`` attribute instead of
defining the full model.

Call the :meth:`~.SQLAlchemy.reflect` method on the extension. It will reflect all the
tables for each bind key. Each metadata's ``tables`` attribute will contain the detected
table objects.

.. code-block:: python

    with app.app_context():
        db.reflect()

    class User:
        __table__ = db.metadatas["auth"].tables["user"]

In most cases, it will be more maintainable to define the model classes yourself. You
only need to define the models and columns you will actually use, even if you're
connecting to a broader schema. IDEs will know the available attributes, and migration
tools like Alembic can detect changes and generate schema migrations.
