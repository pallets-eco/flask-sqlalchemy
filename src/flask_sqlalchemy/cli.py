from __future__ import annotations

import typing as t

import sqlalchemy as sa
from flask import current_app


def add_models_to_shell() -> dict[str, t.Any]:
    """Registered with :meth:`~flask.Flask.shell_context_processor` if
    ``add_models_to_shell`` is enabled. Adds the ``db`` instance and all model classes
    to ``flask shell``. Adds the ``sqlalchemy`` namespace as ``sa`` to ``flask shell``.
    """
    db = current_app.extensions["sqlalchemy"]
    out = {m.class_.__name__: m.class_ for m in db.Model._sa_registry.mappers}
    out["sa"] = sa
    out["db"] = db
    return out
