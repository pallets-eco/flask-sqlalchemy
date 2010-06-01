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
            # TODO: detect methods
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
    return getattr(_request_ctx_stack.top, 'sqlalchemy_queries', [])


class Pagination(object):

    def __init__(self, query, page, per_page, total, items):
        self.query = query
        self.page = page
        self.per_page = per_page
        self.total = total
        self.items = items

    @property
    def pages(self):
        return int(ceil(self.total / float(self.per_page)))

    def prev(self, error_out=False):
        return self.query.paginate(self.page - 1, self.per_page, error_out)

    def have_prev(self):
        return self.page > 1

    def next(self, error_out=False):
        return self.query.paginate(self.page + 1, self.per_page, error_out)

    def have_next(self):
        return self.page < self.pages


class BaseQuery(orm.Query):

    def get_or_404(self, *args, **kwargs):
        rv = self.get(*args, **kwargs)
        if rv is None:
            abort(404)
        return rv

    def paginate(self, page, per_page=20, error_out=True):
        if error_out and page < 1:
            abort(404)
        total_count = self.count()
        items = self.limit(per_page).offset((page - 1) * per_page).all()
        if not items and page != 1 and error_out:
            abort(404)
        return Pagination(self, page, per_page, total, items)


class QueryProperty(object):

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
            if uri == self._connected_for:
                return self._engine
            info = make_url(uri)
            options = {'convert_unicode': True}
            self._sa.apply_driver_hacks(info, options)
            if self._app.debug:
                options['proxy'] = _ConnectionDebugProxy(self._app.import_name)
            self._engine = rv = sqlalchemy.create_engine(info, **options)
            self._engine_for = uri
            return rv


class SQLAlchemy(object):

    def __init__(self, app=None, disable_native_unicode=False):
        self.disable_native_unicode = disable_native_unicode
        self.session = _create_scoped_session(self)

        self.Base = declarative_base()
        self.Base.query_class = BaseQuery
        self.Base.query = QueryProperty(self)

        self._engine_lock = Lock()

        if app is not None:
            self.app = app
            self.init_app(app)
        else:
            self.app = None

        _include_sqlalchemy(self)

    def init_app(self, app):
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite://')
        @app.after_request
        def shutdown_session(response):
            self.session.remove()
            return response

    def apply_driver_hacks(self, info, options):
        if info.drivername == 'mysql':
            info.query.setdefault('charset', 'utf8')
        if self.disable_native_unicode:
            options['use_native_unicode'] = False

    @property
    def engine(self):
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
        self.Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.Base.metadata.drop_all(bind=self.engine)

    def __repr__(self):
        return '<%s engine=%r>' % (
            self.__class__.__name__,
            self.app.config['SQLALCHEMY_DATABASE_URI']
        )
