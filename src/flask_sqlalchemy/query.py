from flask import abort
from sqlalchemy import orm

from .pagination import Pagination


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
        self,
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = None,
        error_out: bool = True,
        count: bool = True,
    ) -> Pagination:
        """Apply an offset and limit to the query based on the current page and number
        of items per page, returning a :class:`.Pagination` object.

        :param query: The query to paginate.
        :param page: The current page, used to calculate the offset. Defaults to the
            ``page`` query arg during a request, or 1 otherwise.
        :param per_page: The maximum number of items on a page, used to calculate the
            offset and limit. Defaults to the ``per_page`` query arg during a request,
            or 20 otherwise.
        :param max_per_page: The maximum allowed value for ``per_page``, to limit a
            user-provided value.
        :param error_out: Abort with a ``404 Not Found`` error if no items are returned
            and ``page`` is not 1, or if ``page`` is less than 1 or ``per_page`` is
            negative, or if either are not ints. If disabled, an invalid ``page``
            defaults to 1, and ``per_page`` defaults to 20.
        :param count: Calculate the total number of values by issuing an extra count
            query. For very complex queries this may be inaccurate or slow, so it can be
            disabled and set manually if necessary.

        .. versionchanged:: 3.0
            All parameters are keyword-only.

        .. versionchanged:: 3.0
            The ``count`` query is more efficient.
        """
        return Pagination.apply_to_query(
            self,
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=error_out,
            count=count,
        )
