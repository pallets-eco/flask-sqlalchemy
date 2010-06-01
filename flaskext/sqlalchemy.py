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
from flask import _request_ctx_stack, abort
from operator import itemgetter
from threading import Lock
from sqlalchemy import orm
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


class BaseQuery(orm.Query):

    def get_or_404(self, *args, **kwargs):
        rv = self.get(*args, **kwargs)
        if rv is None:
            abort(404)
        return rv


class SQLAlchemy(object):

    def __init__(self, app, disable_native_unicode=False):
        app.config.setdefault('SQLALCHEMY_DATABASE_URI', 'sqlite://')
        self.disable_native_unicode = disable_native_unicode
        self.app = app
        self.session = _create_scoped_session(self)
        self.Base = declarative_base()
        self.Base.query = self.session.query_property()

        self._engine = None
        self._engine_for = None
        self._engine_lock = Lock()

        _include_sqlalchemy(self)

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
            uri = self.app.config['SQLALCHEMY_DATABASE_URI']
            if uri == self._engine_for:
                return self._engine
            info = make_url(uri)
            options = {'convert_unicode': True}
            self.apply_driver_hacks(info, options)
            if self.app.debug:
                options['proxy'] = _ConnectionDebugProxy(self.app.import_name)
            self._engine = rv = sqlalchemy.create_engine(info, **options)
            self._engine_for = uri
            return rv

    def create_all(self):
        self.Base.metadata.create_all(bind=self.engine)

    def drop_all(self):
        self.Base.metadata.drop_all(bind=self.engine)

    def __repr__(self):
        return '<%s engine=%r>' % (
            self.__class__.__name__,
            self.app.config['SQLALCHEMY_DATABASE_URI']
        )
