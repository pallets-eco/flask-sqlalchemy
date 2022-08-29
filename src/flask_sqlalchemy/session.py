from sqlalchemy.orm import Session as SessionBase

from .track_modifications import _SessionSignalEvents


class SignallingSession(SessionBase):
    """The signalling session is the default session that Flask-SQLAlchemy
    uses.  It extends the default session system with bind selection and
    modification tracking.

    If you want to use a different session you can override the
    :meth:`SQLAlchemy.create_session` function.

    .. versionadded:: 2.0

    .. versionadded:: 2.1
        The `binds` option was added, which allows a session to be joined
        to an external transaction.
    """

    def __init__(self, db, autocommit=False, autoflush=True, **options):
        #: The application that this session belongs to.
        self.app = app = db.get_app()
        track_modifications = app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]
        bind = options.pop("bind", None) or db.engine
        binds = options.pop("binds", db.get_binds(app))

        if track_modifications:
            _SessionSignalEvents.register(self)

        SessionBase.__init__(
            self,
            autocommit=autocommit,
            autoflush=autoflush,
            bind=bind,
            binds=binds,
            **options,
        )

    def get_bind(self, mapper=None, **kwargs):
        """Return the engine or connection for a given model or
        table, using the ``__bind_key__`` if it is set.
        """
        # mapper is None if someone tries to just get a connection
        if mapper is not None:
            try:
                # SA >= 1.3
                persist_selectable = mapper.persist_selectable
            except AttributeError:
                # SA < 1.3
                persist_selectable = mapper.mapped_table

            info = getattr(persist_selectable, "info", {})
            bind_key = info.get("bind_key")
            if bind_key is not None:
                from .extension import get_state

                state = get_state(self.app)
                return state.db.get_engine(self.app, bind=bind_key)

        return super().get_bind(mapper, **kwargs)
