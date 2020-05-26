Signalling Support
==================

Connect to the following signals to get notified before and after
changes are committed to the database. Tracking changes adds significant
overhead, so it is only enabled if ``SQLALCHEMY_TRACK_MODIFICATIONS`` is
enabled in the config. In most cases, you'll probably be better served
by using `SQLAlchemy events`_ directly.

.. _SQLAlchemy events: https://docs.sqlalchemy.org/core/event.html

.. data:: models_committed

    This signal is sent when changed models are committed to the
    database.

    The sender is the application that emitted the changes. The receiver
    is passed the ``changes`` parameter with a list of tuples in the
    form ``(model instance, operation)``.

    The operation is one of ``'insert'``, ``'update'``, and
    ``'delete'``.

.. data:: before_models_committed

    This signal works exactly like :data:`models_committed` but is
    emitted before the commit takes place.
