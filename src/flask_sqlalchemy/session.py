from __future__ import annotations

import typing as t

import sqlalchemy as sa
import sqlalchemy.exc
import sqlalchemy.orm
from flask.globals import app_ctx

if t.TYPE_CHECKING:
    from .extension import SQLAlchemy


class Session(sa.orm.Session):
    """A SQLAlchemy :class:`~sqlalchemy.orm.Session` class that chooses what engine to
    use based on the bind key associated with the metadata associated with the thing
    being queried.

    To customize ``db.session``, subclass this and pass it as the ``class_`` key in the
    ``session_options`` to :class:`.SQLAlchemy`.

    .. versionchanged:: 3.0
        Renamed from ``SignallingSession``.
    """

    def __init__(self, db: SQLAlchemy, **kwargs: t.Any) -> None:
        super().__init__(**kwargs)
        self._db = db
        self._model_changes: dict[object, tuple[t.Any, str]] = {}

    def get_bind(  # type: ignore[override]
        self,
        mapper: t.Any | None = None,
        clause: t.Any | None = None,
        bind: sa.engine.Engine | sa.engine.Connection | None = None,
        **kwargs: t.Any,
    ) -> sa.engine.Engine | sa.engine.Connection:
        """Select an engine based on the ``bind_key`` of the metadata associated with
        the model or table being queried. If no bind key is set, uses the default bind.

        .. versionchanged:: 3.0
            The implementation more closely matches the base SQLAlchemy implementation.

        .. versionchanged:: 2.1
            Support joining an external transaction.
        """
        if bind is not None:
            return bind

        if mapper is not None:
            try:
                mapper = sa.inspect(mapper)
            except sa.exc.NoInspectionAvailable as e:
                if isinstance(mapper, type):
                    raise sa.orm.exc.UnmappedClassError(mapper) from e

                raise

            clause = mapper.persist_selectable

        engines = self._db.engines

        if isinstance(clause, sa.Table) and "bind_key" in clause.metadata.info:
            key = clause.metadata.info["bind_key"]

            if key not in engines:
                raise sa.exc.UnboundExecutionError(
                    f"Bind key '{key}' is not in 'SQLALCHEMY_BINDS' config."
                )

            return engines[key]

        if None in engines:
            return engines[None]

        return super().get_bind(mapper=mapper, clause=clause, bind=bind, **kwargs)


def _app_ctx_id() -> int:
    """Get the id of the current Flask application context for the session scope."""
    return id(app_ctx._get_current_object())  # type: ignore[attr-defined]
