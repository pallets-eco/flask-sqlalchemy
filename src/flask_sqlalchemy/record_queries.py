import sys
from operator import itemgetter
from time import perf_counter

from flask import _app_ctx_stack
from flask import current_app
from sqlalchemy import event


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
