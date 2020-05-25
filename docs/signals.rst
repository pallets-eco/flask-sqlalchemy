Signalling Support
==================

Connect to the following signals to get notified before and after changes
are committed to the database. These changes are only tracked if
``SQLALCHEMY_TRACK_MODIFICATIONS`` is enabled in the config.

.. data:: models_committed

   This signal is sent when changed models were committed to the database.

   The sender is the application that emitted the changes.
   The receiver is passed the ``changes`` parameter with a list of tuples in the form ``(model instance, operation)``.

   The operation is one of ``'insert'``, ``'update'``, and ``'delete'``.

.. data:: before_models_committed

   This signal works exactly like :data:`models_committed` but is emitted before the commit takes place.
