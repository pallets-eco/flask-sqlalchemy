Signalling Support
==================

.. versionadded:: 0.10

Starting with Flask-SQLAlchemy 0.10 you can now connect to signals to get
notifications when certain things happen.

The following two signals exist:

.. data:: models_committed

   This signal is sent when changed models are committed to the database.
   The `sender` parameter is the application that emitted the changes,
   and the `changes` parameter is a list of tuples in the form
   ``(model, operation identifier)``.

   The model is the instance of the model that was sent to the database
   and the operation is ``'insert'`` when a model was inserted,
   ``'delete'`` when the model was deleted and ``'update'`` if any
   of the columns where updated.

.. data:: before_models_committed

   Works exactly the same as :data:`models_committed` but is emitted
   right before the committing takes place.
