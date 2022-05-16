import functools
import os
import sys
import warnings
from math import ceil
from operator import itemgetter
from threading import Lock
from time import perf_counter

import sqlalchemy
from flask import _app_ctx_stack
from flask import abort
from flask import current_app
from flask import request
from flask.signals import Namespace
from sqlalchemy import event
from sqlalchemy import inspect
from sqlalchemy import orm
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.orm.session import Session as SessionBase

from .model import DefaultMeta
from .model import Model

try:
    from sqlalchemy.orm import declarative_base
    from sqlalchemy.orm import DeclarativeMeta
except ImportError:
    # SQLAlchemy <= 1.3
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.ext.declarative import DeclarativeMeta

# Scope the session to the current greenlet if greenlet is available,
# otherwise fall back to the current thread.
try:
    from greenlet import getcurrent as _ident_func
except ImportError:
    from threading import get_ident as _ident_func

__version__ = "3.0.0.dev0"

_signals = Namespace()
models_committed = _signals.signal("models-committed")
before_models_committed = _signals.signal("before-models-committed")


def _sa_url_set(url, **kwargs):
    try:
        url = url.set(**kwargs)
    except AttributeError:
        # SQLAlchemy <= 1.3
        for key, value in kwargs.items():
            setattr(url, key, value)

    return url


def _sa_url_query_setdefault(url, **kwargs):
    query = dict(url.query)

    for key, value in kwargs.items():
        query.setdefault(key, value)

    return _sa_url_set(url, query=query)


def _make_table(db):
    def _make_table(*args, **kwargs):
        if len(args) > 1 and isinstance(args[1], db.Column):
            args = (args[0], db.metadata) + args[1:]
        info = kwargs.pop("info", None) or {}
        info.setdefault("bind_key", None)
        kwargs["info"] = info
        return sqlalchemy.Table(*args, **kwargs)

    return _make_table


def _set_default_query_class(d, cls):
    if "query_class" not in d:
        d["query_class"] = cls


def _wrap_with_default_query_class(fn, cls):
    @functools.wraps(fn)
    def newfn(*args, **kwargs):
        _set_default_query_class(kwargs, cls)
        if "backref" in kwargs:
            backref = kwargs["backref"]
            if isinstance(backref, str):
                backref = (backref, {})
            _set_default_query_class(backref[1], cls)
        return fn(*args, **kwargs)

    return newfn


def _include_sqlalchemy(obj, cls):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))
    # Note: obj.Table does not attempt to be a SQLAlchemy Table class.
    obj.Table = _make_table(obj)
    obj.relationship = _wrap_with_default_query_class(obj.relationship, cls)
    obj.relation = _wrap_with_default_query_class(obj.relation, cls)
    obj.dynamic_loader = _wrap_with_default_query_class(obj.dynamic_loader, cls)
    obj.event = event


class _DebugQueryTuple(tuple):
    statement = property(itemgetter(0))
    parameters = property(itemgetter(1))
    start_time = property(itemgetter(2))
    end_time = property(itemgetter(3))
    context = property(itemgetter(4))

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __repr__(self):
        return (
            f"<query statement={self.statement!r} parameters={self.parameters!r}"
            f" duration={self.duration:.03f}>"
        )


def _calling_context(app_path):
    frm = sys._getframe(1)
    while frm.f_back is not None:
        name = frm.f_globals.get("__name__")
        if name and (name == app_path or name.startswith(f"{app_path}.")):
            funcname = frm.f_code.co_name
            return f"{frm.f_code.co_filename}:{frm.f_lineno} ({funcname})"
        frm = frm.f_back
    return "<unknown>"


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
                state = get_state(self.app)
                return state.db.get_engine(self.app, bind=bind_key)

        return super().get_bind(mapper, **kwargs)


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


class _EngineDebuggingSignalEvents:
    """Sets up handlers for two events that let us track the execution time of
    queries."""

    def __init__(self, engine, import_name):
        self.engine = engine
        self.app_package = import_name

    def register(self):
        event.listen(self.engine, "before_cursor_execute", self.before_cursor_execute)
        event.listen(self.engine, "after_cursor_execute", self.after_cursor_execute)

    def before_cursor_execute(
        self, conn, cursor, statement, parameters, context, executemany
    ):
        if current_app:
            context._query_start_time = perf_counter()

    def after_cursor_execute(
        self, conn, cursor, statement, parameters, context, executemany
    ):
        if current_app:
            try:
                queries = _app_ctx_stack.top.sqlalchemy_queries
            except AttributeError:
                queries = _app_ctx_stack.top.sqlalchemy_queries = []

            queries.append(
                _DebugQueryTuple(
                    (
                        statement,
                        parameters,
                        context._query_start_time,
                        perf_counter(),
                        _calling_context(self.app_package),
                    )
                )
            )


def get_debug_queries():
    """In debug mode or testing mode, Flask-SQLAlchemy will log all the SQL
    queries sent to the database. This information is available until the end
    of request which makes it possible to easily ensure that the SQL generated
    is the one expected on errors or in unittesting. Alternatively, you can also
    enable the query recording by setting the ``'SQLALCHEMY_RECORD_QUERIES'``
    config variable to `True`.

    The value returned will be a list of named tuples with the following
    attributes:

    `statement`
        The SQL statement issued

    `parameters`
        The parameters for the SQL statement

    `start_time` / `end_time`
        Time the query started / the results arrived.  Please keep in mind
        that the timer function used depends on your platform. These
        values are only useful for sorting or comparing.  They do not
        necessarily represent an absolute timestamp.

    `duration`
        Time the query took in seconds

    `context`
        A string giving a rough estimation of where in your application
        query was issued.  The exact format is undefined so don't try
        to reconstruct filename or function name.
    """
    return getattr(_app_ctx_stack.top, "sqlalchemy_queries", [])


class Pagination:
    """Internal helper class returned by :meth:`BaseQuery.paginate`.  You
    can also construct it from any other SQLAlchemy query object if you are
    working with other libraries.  Additionally it is possible to pass `None`
    as query object in which case the :meth:`prev` and :meth:`next` will
    no longer work.
    """

    def __init__(self, query, page, per_page, total, items):
        #: the unlimited query object that was used to create this
        #: pagination object.
        self.query = query
        #: the current page number (1 indexed)
        self.page = page
        #: the number of items to be displayed on a page.
        self.per_page = per_page
        #: the total number of items matching the query
        self.total = total
        #: the items for the current page
        self.items = items

    @property
    def pages(self):
        """The total number of pages"""
        if self.per_page == 0 or self.total is None:
            pages = 0
        else:
            pages = int(ceil(self.total / float(self.per_page)))
        return pages

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        assert (
            self.query is not None
        ), "a query object is required for this method to work"
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        if not self.has_prev:
            return None
        return self.page - 1

    @property
    def has_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        assert (
            self.query is not None
        ), "a query object is required for this method to work"
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    @property
    def has_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        if not self.has_next:
            return None
        return self.page + 1

    def iter_pages(self, left_edge=2, left_current=2, right_current=5, right_edge=2):
        """Iterates over the page numbers in the pagination.  The four
        parameters control the thresholds how many numbers should be produced
        from the sides.  Skipped page numbers are represented as `None`.
        This is how you could render such a pagination in the templates:

        .. sourcecode:: html+jinja

            {% macro render_pagination(pagination, endpoint) %}
              <div class=pagination>
              {%- for page in pagination.iter_pages() %}
                {% if page %}
                  {% if page != pagination.page %}
                    <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
                  {% else %}
                    <strong>{{ page }}</strong>
                  {% endif %}
                {% else %}
                  <span class=ellipsis>…</span>
                {% endif %}
              {%- endfor %}
              </div>
            {% endmacro %}
        """
        last = 0
        for num in range(1, self.pages + 1):
            if (
                num <= left_edge
                or (
                    num > self.page - left_current - 1
                    and num < self.page + right_current
                )
                or num > self.pages - right_edge
            ):
                if last + 1 != num:
                    yield None
                yield num
                last = num


class BaseQuery(orm.Query):
    """SQLAlchemy :class:`~sqlalchemy.orm.query.Query` subclass with
    convenience methods for querying in a web application.

    This is the default :attr:`~Model.query` object used for models, and
    exposed as :attr:`~SQLAlchemy.Query`. Override the query class for
    an individual model by subclassing this and setting
    :attr:`~Model.query_class`.
    """

    def get_or_404(self, ident, description=None):
        """Like :meth:`get` but aborts with 404 if not found instead of
        returning ``None``.
        """
        rv = self.get(ident)
        if rv is None:
            abort(404, description=description)
        return rv

    def first_or_404(self, description=None):
        """Like :meth:`first` but aborts with 404 if not found instead
        of returning ``None``.
        """
        rv = self.first()
        if rv is None:
            abort(404, description=description)
        return rv

    def paginate(
        self, page=None, per_page=None, error_out=True, max_per_page=None, count=True
    ):
        """Returns ``per_page`` items from page ``page``.

        If ``page`` or ``per_page`` are ``None``, they will be retrieved from
        the request query. If ``max_per_page`` is specified, ``per_page`` will
        be limited to that value. If there is no request or they aren't in the
        query, they default to 1 and 20 respectively. If ``count`` is ``False``,
        no query to help determine total page count will be run.

        When ``error_out`` is ``True`` (default), the following rules will
        cause a 404 response:

        * No items are found and ``page`` is not 1.
        * ``page`` is less than 1, or ``per_page`` is negative.
        * ``page`` or ``per_page`` are not ints.

        When ``error_out`` is ``False``, ``page`` and ``per_page`` default to
        1 and 20 respectively.

        Returns a :class:`Pagination` object.
        """

        if request:
            if page is None:
                try:
                    page = int(request.args.get("page", 1))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    page = 1

            if per_page is None:
                try:
                    per_page = int(request.args.get("per_page", 20))
                except (TypeError, ValueError):
                    if error_out:
                        abort(404)

                    per_page = 20
        else:
            if page is None:
                page = 1

            if per_page is None:
                per_page = 20

        if max_per_page is not None:
            per_page = min(per_page, max_per_page)

        if page < 1:
            if error_out:
                abort(404)
            else:
                page = 1

        if per_page < 0:
            if error_out:
                abort(404)
            else:
                per_page = 20

        items = self.limit(per_page).offset((page - 1) * per_page).all()

        if not items and page != 1 and error_out:
            abort(404)

        if not count:
            total = None
        else:
            total = self.order_by(None).count()

        return Pagination(self, page, per_page, total, items)


class _QueryProperty:
    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            if mapper:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


def _record_queries(app):
    if app.debug:
        return True
    rq = app.config["SQLALCHEMY_RECORD_QUERIES"]
    if rq is not None:
        return rq
    return bool(app.config.get("TESTING"))


class _EngineConnector:
    def __init__(self, sa, app, bind=None):
        self._sa = sa
        self._app = app
        self._engine = None
        self._connected_for = None
        self._bind = bind
        self._lock = Lock()

    def get_uri(self):
        if self._bind is None:
            return self._app.config["SQLALCHEMY_DATABASE_URI"]
        binds = self._app.config.get("SQLALCHEMY_BINDS") or ()
        assert (
            self._bind in binds
        ), f"Bind {self._bind!r} is not configured in 'SQLALCHEMY_BINDS'."
        return binds[self._bind]

    def get_engine(self):
        with self._lock:
            uri = self.get_uri()
            echo = self._app.config["SQLALCHEMY_ECHO"]
            if (uri, echo) == self._connected_for:
                return self._engine

            sa_url = make_url(uri)
            sa_url, options = self.get_options(sa_url, echo)
            self._engine = rv = self._sa.create_engine(sa_url, options)

            if _record_queries(self._app):
                _EngineDebuggingSignalEvents(
                    self._engine, self._app.import_name
                ).register()

            self._connected_for = (uri, echo)

            return rv

    def get_options(self, sa_url, echo):
        options = {}
        sa_url, options = self._sa.apply_driver_hacks(self._app, sa_url, options)

        if echo:
            options["echo"] = echo

        # Give the config options set by a developer explicitly priority
        # over decisions FSA makes.
        options.update(self._app.config["SQLALCHEMY_ENGINE_OPTIONS"])
        # Give options set in SQLAlchemy.__init__() ultimate priority
        options.update(self._sa._engine_options)
        return sa_url, options


def get_state(app):
    """Gets the state for the application"""
    assert "sqlalchemy" in app.extensions, (
        "The sqlalchemy extension was not registered to the current "
        "application.  Please make sure to call init_app() first."
    )
    return app.extensions["sqlalchemy"]


class _SQLAlchemyState:
    """Remembers configuration for the (db, app) tuple."""

    def __init__(self, db):
        self.db = db
        self.connectors = {}


class SQLAlchemy:
    """This class is used to control the SQLAlchemy integration to one
    or more Flask applications.  Depending on how you initialize the
    object it is usable right away or will attach as needed to a
    Flask application.

    There are two usage modes which work very similarly.  One is binding
    the instance to a very specific Flask application::

        app = Flask(__name__)
        db = SQLAlchemy(app)

    The second possibility is to create the object once and configure the
    application later to support it::

        db = SQLAlchemy()

        def create_app():
            app = Flask(__name__)
            db.init_app(app)
            return app

    The difference between the two is that in the first case methods like
    :meth:`create_all` and :meth:`drop_all` will work all the time but in
    the second case a :meth:`flask.Flask.app_context` has to exist.

    By default Flask-SQLAlchemy will apply some backend-specific settings
    to improve your experience with them.

    This class also provides access to all the SQLAlchemy functions and classes
    from the :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` modules.  So you can
    declare models like this::

        class User(db.Model):
            username = db.Column(db.String(80), unique=True)
            pw_hash = db.Column(db.String(80))

    You can still use :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` directly, but
    note that Flask-SQLAlchemy customizations are available only through an
    instance of this :class:`SQLAlchemy` class.  Query classes default to
    :class:`BaseQuery` for `db.Query`, `db.Model.query_class`, and the default
    query_class for `db.relationship` and `db.backref`.  If you use these
    interfaces through :mod:`sqlalchemy` and :mod:`sqlalchemy.orm` directly,
    the default query class will be that of :mod:`sqlalchemy`.

    .. admonition:: Check types carefully

       Don't perform type or `isinstance` checks against `db.Table`, which
       emulates `Table` behavior but is not a class. `db.Table` exposes the
       `Table` interface, but is a function which allows omission of metadata.

    The ``session_options`` parameter, if provided, is a dict of parameters
    to be passed to the session constructor. See
    :class:`~sqlalchemy.orm.session.Session` for the standard options.

    The ``engine_options`` parameter, if provided, is a dict of parameters
    to be passed to create engine.  See :func:`~sqlalchemy.create_engine`
    for the standard options.  The values given here will be merged with and
    override anything set in the ``'SQLALCHEMY_ENGINE_OPTIONS'`` config
    variable or othewise set by this library.

    .. versionchanged:: 3.0
        Removed the ``use_native_unicode`` parameter and config.

    .. versionchanged:: 3.0
        ``COMMIT_ON_TEARDOWN`` is deprecated and will be removed in
        version 3.1. Call ``db.session.commit()`` directly instead.

    .. versionchanged:: 2.4
        Added the ``engine_options`` parameter.

    .. versionchanged:: 2.1
        Added the ``metadata`` parameter. This allows for setting custom
        naming conventions among other, non-trivial things.

    .. versionchanged:: 2.1
        Added the ``query_class`` parameter, to allow customisation
        of the query class, in place of the default of
        :class:`BaseQuery`.

    .. versionchanged:: 2.1
        Added the ``model_class`` parameter, which allows a custom model
        class to be used in place of :class:`Model`.

    .. versionchanged:: 2.1
        Use the same query class across ``session``, ``Model.query`` and
        ``Query``.

    .. versionchanged:: 0.16
        ``scopefunc`` is now accepted on ``session_options``. It allows
        specifying a custom function which will define the SQLAlchemy
        session's scoping.

    .. versionchanged:: 0.10
        Added the ``session_options`` parameter.
    """

    #: Default query class used by :attr:`Model.query` and other queries.
    #: Customize this by passing ``query_class`` to :func:`SQLAlchemy`.
    #: Defaults to :class:`BaseQuery`.
    Query = None

    def __init__(
        self,
        app=None,
        session_options=None,
        metadata=None,
        query_class=BaseQuery,
        model_class=Model,
        engine_options=None,
    ):

        self.Query = query_class
        self.session = self.create_scoped_session(session_options)
        self.Model = self.make_declarative_base(model_class, metadata)
        self._engine_lock = Lock()
        self.app = app
        self._engine_options = engine_options or {}
        _include_sqlalchemy(self, query_class)

        if app is not None:
            self.init_app(app)

    @property
    def metadata(self):
        """The metadata associated with ``db.Model``."""

        return self.Model.metadata

    def create_scoped_session(self, options=None):
        """Create a :class:`~sqlalchemy.orm.scoping.scoped_session`
        on the factory from :meth:`create_session`.

        An extra key ``'scopefunc'`` can be set on the ``options`` dict to
        specify a custom scope function.  If it's not provided, Flask's app
        context stack identity is used. This will ensure that sessions are
        created and removed with the request/response cycle, and should be fine
        in most cases.

        :param options: dict of keyword arguments passed to session class  in
            ``create_session``
        """

        if options is None:
            options = {}

        scopefunc = options.pop("scopefunc", _ident_func)
        options.setdefault("query_cls", self.Query)
        return orm.scoped_session(self.create_session(options), scopefunc=scopefunc)

    def create_session(self, options):
        """Create the session factory used by :meth:`create_scoped_session`.

        The factory **must** return an object that SQLAlchemy recognizes as a session,
        or registering session events may raise an exception.

        Valid factories include a :class:`~sqlalchemy.orm.session.Session`
        class or a :class:`~sqlalchemy.orm.session.sessionmaker`.

        The default implementation creates a ``sessionmaker`` for
        :class:`SignallingSession`.

        :param options: dict of keyword arguments passed to session class
        """

        return orm.sessionmaker(class_=SignallingSession, db=self, **options)

    def make_declarative_base(self, model, metadata=None):
        """Creates the declarative base that all models will inherit from.

        :param model: base model class (or a tuple of base classes) to pass
            to :func:`~sqlalchemy.ext.declarative.declarative_base`. Or a class
            returned from ``declarative_base``, in which case a new base class
            is not created.
        :param metadata: :class:`~sqlalchemy.MetaData` instance to use, or
            none to use SQLAlchemy's default.

        .. versionchanged 2.3.0::
            ``model`` can be an existing declarative base in order to support
            complex customization such as changing the metaclass.
        """
        if not isinstance(model, DeclarativeMeta):
            model = declarative_base(
                cls=model, name="Model", metadata=metadata, metaclass=DefaultMeta
            )

        # if user passed in a declarative base and a metaclass for some reason,
        # make sure the base uses the metaclass
        if metadata is not None and model.metadata is not metadata:
            model.metadata = metadata

        if not getattr(model, "query_class", None):
            model.query_class = self.Query

        model.query = _QueryProperty(self)
        return model

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup.  Never use a database in the context
        of an application not initialized that way or connections will
        leak.
        """

        # We intentionally don't set self.app = app, to support multiple
        # applications. If the app is passed in the constructor,
        # we set it and don't support multiple applications.
        if not (
            app.config.get("SQLALCHEMY_DATABASE_URI")
            or app.config.get("SQLALCHEMY_BINDS")
        ):
            raise RuntimeError(
                "Either SQLALCHEMY_DATABASE_URI or SQLALCHEMY_BINDS needs to be set."
            )

        app.config.setdefault("SQLALCHEMY_DATABASE_URI", None)
        app.config.setdefault("SQLALCHEMY_BINDS", None)
        app.config.setdefault("SQLALCHEMY_ECHO", False)
        app.config.setdefault("SQLALCHEMY_RECORD_QUERIES", None)
        app.config.setdefault("SQLALCHEMY_COMMIT_ON_TEARDOWN", False)
        app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)
        app.config.setdefault("SQLALCHEMY_ENGINE_OPTIONS", {})

        app.extensions["sqlalchemy"] = _SQLAlchemyState(self)

        @app.teardown_appcontext
        def shutdown_session(response_or_exc):
            if app.config["SQLALCHEMY_COMMIT_ON_TEARDOWN"]:
                warnings.warn(
                    "'COMMIT_ON_TEARDOWN' is deprecated and will be"
                    " removed in version 3.1. Call"
                    " 'db.session.commit()'` directly instead.",
                    DeprecationWarning,
                )

                if response_or_exc is None:
                    self.session.commit()

            self.session.remove()
            return response_or_exc

    def apply_driver_hacks(self, app, sa_url, options):
        """This method is called before engine creation and used to inject
        driver specific hacks into the options.  The `options` parameter is
        a dictionary of keyword arguments that will then be used to call
        the :func:`sqlalchemy.create_engine` function.

        The default implementation provides some defaults for things
        like pool sizes for MySQL and SQLite.

        .. versionchanged:: 3.0
            Change the default MySQL character set to "utf8mb4".

        .. versionchanged:: 2.5
            Returns ``(sa_url, options)``. SQLAlchemy 1.4 made the URL
            immutable, so any changes to it must now be passed back up
            to the original caller.
        """
        if sa_url.drivername.startswith("mysql"):
            sa_url = _sa_url_query_setdefault(sa_url, charset="utf8mb4")

            if sa_url.drivername != "mysql+gaerdbms":
                options.setdefault("pool_size", 10)
                options.setdefault("pool_recycle", 7200)
        elif sa_url.drivername == "sqlite":
            pool_size = options.get("pool_size")
            detected_in_memory = False
            if sa_url.database in (None, "", ":memory:"):
                detected_in_memory = True
                from sqlalchemy.pool import StaticPool

                options["poolclass"] = StaticPool
                if "connect_args" not in options:
                    options["connect_args"] = {}
                options["connect_args"]["check_same_thread"] = False

                # we go to memory and the pool size was explicitly set
                # to 0 which is fail.  Let the user know that
                if pool_size == 0:
                    raise RuntimeError(
                        "SQLite in memory database with an "
                        "empty queue not possible due to data "
                        "loss."
                    )
            # if pool size is None or explicitly set to 0 we assume the
            # user did not want a queue for this sqlite connection and
            # hook in the null pool.
            elif not pool_size:
                from sqlalchemy.pool import NullPool

                options["poolclass"] = NullPool

            # If the database path is not absolute, it's relative to the
            # app instance path, which might need to be created.
            if not detected_in_memory and not os.path.isabs(sa_url.database):
                os.makedirs(app.instance_path, exist_ok=True)
                sa_url = _sa_url_set(
                    sa_url, database=os.path.join(app.root_path, sa_url.database)
                )

        return sa_url, options

    @property
    def engine(self):
        """Gives access to the engine.  If the database configuration is bound
        to a specific application (initialized with an application) this will
        always return a database connection.  If however the current application
        is used this might raise a :exc:`RuntimeError` if no application is
        active at the moment.
        """
        return self.get_engine()

    def make_connector(self, app=None, bind=None):
        """Creates the connector for a given state and bind."""
        return _EngineConnector(self, self.get_app(app), bind)

    def get_engine(self, app=None, bind=None):
        """Returns a specific engine."""

        app = self.get_app(app)
        state = get_state(app)

        with self._engine_lock:
            connector = state.connectors.get(bind)

            if connector is None:
                connector = self.make_connector(app, bind)
                state.connectors[bind] = connector

            return connector.get_engine()

    def create_engine(self, sa_url, engine_opts):
        """Override this method to have final say over how the
        SQLAlchemy engine is created.

        In most cases, you will want to use
        ``'SQLALCHEMY_ENGINE_OPTIONS'`` config variable or set
        ``engine_options`` for :func:`SQLAlchemy`.
        """
        return sqlalchemy.create_engine(sa_url, **engine_opts)

    def get_app(self, reference_app=None):
        """Helper method that implements the logic to look up an
        application."""

        if reference_app is not None:
            return reference_app

        if current_app:
            return current_app._get_current_object()

        if self.app is not None:
            return self.app

        raise RuntimeError(
            "No application found. Either work inside a view function or push"
            " an application context. See"
            " https://flask-sqlalchemy.palletsprojects.com/contexts/."
        )

    def get_tables_for_bind(self, bind=None):
        """Returns a list of all tables relevant for a bind."""
        result = []
        for table in self.Model.metadata.tables.values():
            if table.info.get("bind_key") == bind:
                result.append(table)
        return result

    def get_binds(self, app=None):
        """Returns a dictionary with a table->engine mapping.

        This is suitable for use of sessionmaker(binds=db.get_binds(app)).
        """
        app = self.get_app(app)
        binds = [None] + list(app.config.get("SQLALCHEMY_BINDS") or ())
        retval = {}
        for bind in binds:
            engine = self.get_engine(app, bind)
            tables = self.get_tables_for_bind(bind)
            retval.update({table: engine for table in tables})
        return retval

    def _execute_for_all_tables(self, app, bind, operation, skip_tables=False):
        app = self.get_app(app)

        if bind == "__all__":
            binds = [None] + list(app.config.get("SQLALCHEMY_BINDS") or ())
        elif isinstance(bind, str) or bind is None:
            binds = [bind]
        else:
            binds = bind

        for bind in binds:
            extra = {}
            if not skip_tables:
                tables = self.get_tables_for_bind(bind)
                extra["tables"] = tables
            if operation == "reflect":
                extra["info"] = {"bind_key": bind}
            op = getattr(self.Model.metadata, operation)
            op(bind=self.get_engine(app, bind), **extra)

    def create_all(self, bind="__all__", app=None):
        """Create all tables that do not already exist in the database.
        This does not update existing tables, use a migration library
        for that.

        :param bind: A bind key or list of keys to create the tables
            for. Defaults to all binds.
        :param app: Use this app instead of requiring an app context.

        .. versionchanged:: 0.12
            Added the ``bind`` and ``app`` parameters.
        """
        self._execute_for_all_tables(app, bind, "create_all")

    def drop_all(self, bind="__all__", app=None):
        """Drop all tables.

        :param bind: A bind key or list of keys to drop the tables for.
            Defaults to all binds.
        :param app: Use this app instead of requiring an app context.

        .. versionchanged:: 0.12
            Added the ``bind`` and ``app`` parameters.
        """
        self._execute_for_all_tables(app, bind, "drop_all")

    def reflect(self, bind="__all__", app=None):
        """Reflects tables from the database.

        :param bind: A bind key or list of keys to reflect the tables
            from. Defaults to all binds.
        :param app: Use this app instead of requiring an app context.

        .. versionchanged:: 0.12
            Added the ``bind`` and ``app`` parameters.
        """
        self._execute_for_all_tables(app, bind, "reflect", skip_tables=True)

    def __repr__(self):
        url = self.engine.url if self.app or current_app else None
        return f"<{type(self).__name__} engine={url!r}>"
