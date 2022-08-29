from flask.signals import Namespace
from sqlalchemy import event
from sqlalchemy import inspect

_signals = Namespace()
models_committed = _signals.signal("models-committed")
before_models_committed = _signals.signal("before-models-committed")


class _SessionSignalEvents:
    @classmethod
    def register(cls, session):
        if not hasattr(session, "_model_changes"):
            session._model_changes = {}

        event.listen(session, "before_flush", cls.record_ops)
        event.listen(session, "before_commit", cls.record_ops)
        event.listen(session, "before_commit", cls.before_commit)
        event.listen(session, "after_commit", cls.after_commit)
        event.listen(session, "after_rollback", cls.after_rollback)

    @classmethod
    def unregister(cls, session):
        if hasattr(session, "_model_changes"):
            del session._model_changes

        event.remove(session, "before_flush", cls.record_ops)
        event.remove(session, "before_commit", cls.record_ops)
        event.remove(session, "before_commit", cls.before_commit)
        event.remove(session, "after_commit", cls.after_commit)
        event.remove(session, "after_rollback", cls.after_rollback)

    @staticmethod
    def record_ops(session, flush_context=None, instances=None):
        try:
            d = session._model_changes
        except AttributeError:
            return

        for targets, operation in (
            (session.new, "insert"),
            (session.dirty, "update"),
            (session.deleted, "delete"),
        ):
            for target in targets:
                state = inspect(target)
                key = state.identity_key if state.has_identity else id(target)
                d[key] = (target, operation)

    @staticmethod
    def before_commit(session):
        try:
            d = session._model_changes
        except AttributeError:
            return

        if d:
            before_models_committed.send(session.app, changes=list(d.values()))

    @staticmethod
    def after_commit(session):
        try:
            d = session._model_changes
        except AttributeError:
            return

        if d:
            models_committed.send(session.app, changes=list(d.values()))
            d.clear()

    @staticmethod
    def after_rollback(session):
        try:
            d = session._model_changes
        except AttributeError:
            return

        d.clear()
