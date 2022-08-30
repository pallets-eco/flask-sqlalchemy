from __future__ import annotations

import typing as t

import sqlalchemy as sa
import sqlalchemy.event
from flask import current_app
from flask import has_app_context
from flask.signals import Namespace

if t.TYPE_CHECKING:
    from .session import SignallingSession

_signals = Namespace()
models_committed = _signals.signal("models-committed")
before_models_committed = _signals.signal("before-models-committed")


def _listen(session) -> None:
    sa.event.listen(session, "before_flush", _record_ops, named=True)
    sa.event.listen(session, "before_commit", _record_ops, named=True)
    sa.event.listen(session, "before_commit", _before_commit)
    sa.event.listen(session, "after_commit", _after_commit)
    sa.event.listen(session, "after_rollback", _after_rollback)


def _record_ops(session: SignallingSession, **kwargs: t.Any) -> None:
    if not has_app_context():
        return

    if not current_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]:
        return

    for targets, operation in (
        (session.new, "insert"),
        (session.dirty, "update"),
        (session.deleted, "delete"),
    ):
        for target in targets:
            state = sa.inspect(target)
            key = state.identity_key if state.has_identity else id(target)
            session._model_changes[key] = (target, operation)


def _before_commit(session: SignallingSession) -> None:
    if not has_app_context():
        return

    if not current_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]:
        return

    if session._model_changes:
        changes = list(session._model_changes.values())
        before_models_committed.send(current_app._get_current_object(), changes=changes)


def _after_commit(session: SignallingSession) -> None:
    if not has_app_context():
        return

    if not current_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]:
        return

    if session._model_changes:
        changes = list(session._model_changes.values())
        models_committed.send(current_app._get_current_object(), changes=changes)
        session._model_changes.clear()


def _after_rollback(session: SignallingSession) -> None:
    session._model_changes.clear()
