Tracking Modifications
======================

.. warning::
    Tracking changes adds significant overhead. In most cases, you'll be better served by
    using `SQLAlchemy events`_ directly.

.. _SQLAlchemy events: https://docs.sqlalchemy.org/core/event.html

Flask-SQLAlchemy can set up its session to track inserts, updates, and deletes for
models, then send a Blinker signal with a list of these changes either before or during
calls to ``session.flush()`` and ``session.commit()``.

To enable this feature, set :data:`.SQLALCHEMY_TRACK_MODIFICATIONS` in the Flask app
config. Then add a listener to :data:`.models_committed` (emitted after the commit) or
:data:`.before_models_committed` (emitted before the commit).

.. code-block:: python

    from flask_sqlalchemy.track_modifications import models_committed

    def get_modifications(sender: Flask, changes: list[tuple[t.Any, str]]) -> None:
        ...

    models_committed.connect(get_modifications)
