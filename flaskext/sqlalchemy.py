# -*- coding: utf-8 -*-
"""
    flaskext.sqlalchemy
    ~~~~~~~~~~~~~~~~~~~

    Adds basic SQLAlchemy support to your application.

    :copyright: (c) 2010 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
from __future__ import with_statement, absolute_import
import sys
import time
import sqlalchemy
from math import ceil
from types import MethodType
from flask import _request_ctx_stack, abort
from operator import itemgetter
from threading import Lock
from sqlalchemy import orm
from sqlalchemy.orm.exc import UnmappedClassError
from sqlalchemy.interfaces import ConnectionProxy
from sqlalchemy.engine.url import make_url
from sqlalchemy.ext.declarative import declarative_base

# the best timer function for the platform
if sys.platform == 'win32':
    _timer = time.clock
else:
    _timer = time.time


def _create_scoped_session(db):
    return orm.scoped_session(lambda: orm.create_session(autocommit=False,
                                                         autoflush=False,
                                                         bind=db.engine))


def _include_sqlalchemy(obj):
    for module in sqlalchemy, sqlalchemy.orm:
        for key in module.__all__:
            if not hasattr(obj, key):
                setattr(obj, key, getattr(module, key))


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
        return '<query statement="%s" parameters=%r duration=%.03f>' % (
            self.statement,
            self.parameters,
            self.duration
        )


def _calling_context(app_path):
    frm = sys._getframe(1)
    while frm.f_back is not None:
        name = frm.f_globals.get('__name__')
        if name and (name == app_path or name.startswith(app_path + '.')):
            funcname = frm.f_code.co_name
            return '%s:%s (%s)' % (
                frm.f_code.co_filename,
                frm.f_lineno,
                funcname
            )
        frm = frm.f_back
    return '<unknown>'


class _ConnectionDebugProxy(ConnectionProxy):
    """Helps debugging the database."""

    def __init__(self, import_name):
        self.app_package = import_name

    def cursor_execute(self, execute, cursor, statement, parameters,
                       context, executemany):
        start = _timer()
        try:
            return execute(cursor, statement, parameters, context)
        finally:
            ctx = _request_ctx_stack.top
            if ctx is not None:
                queries = getattr(ctx, 'sqlalchemy_queries', None)
                if queries is None:
                    queries = []
                    setattr(ctx, 'sqlalchemy_queries', queries)
                queries.append(_DebugQueryTuple((
                    statement, parameters, start, _timer(),
                    _calling_context(self.app_package))))


def get_debug_queries():
    """In debug mode Flask-SQLAlchemy will log all the SQL queries sent
    to the database.  This information is available until the end of request
    which makes it possible to easily ensure that the SQL generated is the
    one expected on errors or in unittesting.  If you don't want to enable
    the DEBUG mode for your unittests you can also enable the query
    recording by setting the ``'SQLALCHEMY_RECORD_QUERIES'`` config variable
    to `True`.

    The value returned will be a list of named tuples with the following
    attributes:

    `statement`
        The SQL statement issued

    `parameters`
        The parameters for the SQL statement

    `start_time` / `end_time`
        Time the query started / the results arrived.  Please keep in mind
        that the timer function used for your platform might different this
        values are only useful for sorting or comparing.  They do not
        necessarily represent an absolute timestamp.

    `duration`
        Time the query took in seconds

    `context`
        A string giving a rough estimation of where in your application
        query was issued.  The exact format is undefined so don't try
        to reconstruct filename or function name.
    """
    return getattr(_request_ctx_stack.top, 'sqlalchemy_queries', [])


class Pagination(object):
    """Internal helper class returned by :meth:`BaseQuery.paginate`."""

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
        return int(ceil(self.total / float(self.per_page)))

    def prev(self, error_out=False):
        """Returns a :class:`Pagination` object for the previous page."""
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    @property
    def prev_num(self):
        """Number of the previous page."""
        return self.page - 1

    def have_prev(self):
        """True if a previous page exists"""
        return self.page > 1

    def next(self, error_out=False):
        """Returns a :class:`Pagination` object for the next page."""
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    def have_next(self):
        """True if a next page exists."""
        return self.page < self.pages

    @property
    def next_num(self):
        """Number of the next page"""
        return self.page + 1


class BaseQuery(orm.Query):
    """The default query object used for models.  This can be subclassed and
    replaced for individual models by setting the :attr:`~Model.query_class`
    attribute.  This is a subclass of a standard SQLAlchemy
    :class:`~sqlalchemy.orm.query.Query` class and has all the methods of a
    standard query as well.
    """

    def get_or_404(self, ident):
        """Like :meth:`get` but aborts with 404 if not found instead of
        returning `None`.
        """
        rv = self.get(ident)
        if rv is None:
            abort(404)
        return rv

    def first_or_404(self):
        """Like :meth:`first` but aborts with 404 if not found instead of
        returning `None`.
        """
        rv = self.first()
        if rv is None:
            abort(404)
        return rv

    def paginate(self, page, per_page=20, error_out=True):
        """Returns `per_page` items from page `page`.  By default it will
        abort with 404 if no items were found and the page was larger than
        1.  This behavor can be disabled by setting `error_out` to `False`.

        Returns an :class:`Pagination` object.
        """
        if error_out and page < 1:
            abort(404)
        items = self.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            abort(404)
        return Pagination(self, page, per_page, self.count(), items)


class _QueryProperty(object):

    def __init__(self, sa):
        self.sa = sa

    def __get__(self, obj, type):
        try:
            mapper = orm.class_mapper(type)
            ctx = _request_ctx_stack.top
            if mapper and ctx is not None:
                return type.query_class(mapper, session=self.sa.session())
        except UnmappedClassError:
            return None


class _EngineConnector(object):

    def __init__(self, sa, app):
        self._sa = sa
        self._app = app
        self._engine = None
        self._connected_for = None
        self._lock = Lock()

    def get_engine(self):
        with self._lock:
            uri = self._app.config['SQLALCHEMY_DATABASE_URI']
            echo = self._app.config['SQLALCHEMY_ECHO']
            if (uri, echo) == self._connected_for:
                return self._engine
            info = make_url(uri)
            options = {'convert_unicode': True}
            self._sa.apply_driver_hacks(info, options)
            if self._app.debug or \
               self._app.config['SQLALCHEMY_RECORD_QUERIES']:
                options['proxy'] = _ConnectionDebugProxy(self._app.import_name)
            if echo:
                options['echo'] = True
            self._engine = rv = sqlalchemy.create_engine(info, **options)
            self._connected_for = (uri, echo)
            return rv


class Model(object):
    """Baseclass for custom user models."""

    #: the query class used.  The :attr:`query` attribute is an instance
    #: of this class.  By default a :class:`BaseQuery` is used.
    query_class = BaseQuery

    #: an instance of :attr:`query_class`.  Can be used to query the
    #: database for instances of this model.
    query = None


class SQLAlchemy(object):
    """This class is used to control the SQLAlchemy integration to one
    or more Flask applications.  Depending on how you initialize the
    object it is usable right away or will attach as needed to a
    Flask application.

    There are two usage modes which work very similar.  One is binding
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
    the section case a :meth:`flask.Flask.request_context` has to exist.

    By default Flask-SQLAlchemy will apply some backend-specific settings
    to improve your experience with them.  As of SQLAlchemy 0.6 SQLAlchemy
    will probe the library for native unicode support.  If it detects
    unicode it will let the library handle that, otherwise do that itself.
    Sometimes this detection can fail in which case you might want to set
    `use_native_unicode` to `False`.
    """

    def __init__(self, app=None, use_native_unicode=True):
        self.use_native_unicode = use_native_unicode
        self.session = _create_scoped_session(self)

        self.Model = declarative_base(cls=Model, name='Model')
        self.Model.query = _QueryProperty(self)

        self._engine_lock = Lock()

        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

        _include_sqlalchemy(self)

    def init_app(self, app):
        """This callback can be used to initialize an application for the
        use with this database setup.  Never use a database in the context
        of an application not initialized that way or connections will
        leak.
        """
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite://')
        app.config.setdefault('SQLALCHEMY_ECHO', False)
        app.config.setdefault('SQLALCHEMY_RECORD_QUERIES', False)

        @app.after_request
        def shutdown_session(response):
            self.session.remove()
            return response

    def apply_driver_hacks(self, info, options):
        if info.drivername == 'mysql':
            info.query.setdefault('charset', 'utf8')
        if not self.use_native_unicode:
            options['use_native_unicode'] = False

    @property
    def engine(self):
        """Gives access to the engine.  If the database configuration is bound
        to a specific application (initialized with an application) this will
        always return a database connection.  If however the current application
        is used this might raise a :exc:`RuntimeError` if no application is
        active at the moment.
        """
        with self._engine_lock:
            if self.app is not None:
                app = self.app
            else:
                ctx = _request_ctx_stack.top
                if ctx is not None:
                    app = ctx.app
                else:
                    raise RuntimeError('application not registered on db '
                                       'instance and no application bound '
                                       'to current context')
            connector = getattr(app, '_sqlalchemy_connector', None)
            if connector is None:
                connector = _EngineConnector(self, app)
                app._sqlalchemy_connector = connector
            return connector.get_engine()

    def create_all(self):
        """Creates all tables."""
        self.Model.metadata.create_all(bind=self.engine)

    def drop_all(self):
        """Drops all tables."""
        self.Model.metadata.drop_all(bind=self.engine)

    def reflect(self):
        """Reflects tables from the database."""
        self.Model.metadata.reflect(bind=self.engine)

    def __repr__(self):
        return '<%s engine=%r>' % (
            self.__class__.__name__,
            self.app.config['SQLALCHEMY_DATABASE_URI']
        )
