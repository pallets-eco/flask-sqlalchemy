from __future__ import annotations

import typing as t
from math import ceil

import sqlalchemy as sa
import sqlalchemy.orm
from flask import abort
from flask import request


class Pagination:
    """Returned by :meth:`.Query.paginate`, this describes the current page of data.

    :param query: The original query that was paginated.
    :param page: The current page.
    :param per_page: The maximum number of items on a page.
    :param total: The total number of items across all pages.
    :param items: The items on the current page.

    .. versionchanged:: 3.0
        All parameters are keyword-only.

    .. versionchanged:: 3.0
        Iterating over a pagination object iterates over its items.
    """

    def __init__(
        self,
        *,
        query: sa.orm.Query[t.Any] | None,
        page: int,
        per_page: int,
        total: int | None,
        items: list[t.Any],
    ) -> None:
        self.query = query
        """The original query that was paginated. This is used to produce :meth:`next`
        and :meth:`prev` pages.
        """

        self.page = page
        """The current page."""

        self.per_page = per_page
        """The maximum number of items on a page."""

        self.total = total
        """The total number of items across all pages."""

        self.items = items
        """The items on the current page. Iterating over the pagination object is
        equivalent to iterating over the items.
        """

    @staticmethod
    def _prepare_args(
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = None,
        error_out: bool = True,
    ) -> tuple[int, int]:
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

        if per_page < 1:
            if error_out:
                abort(404)
            else:
                per_page = 20

        return page, per_page

    @classmethod
    def apply_to_query(
        cls,
        query: sa.orm.Query[t.Any],
        *,
        page: int | None = None,
        per_page: int | None = None,
        max_per_page: int | None = 100,
        error_out: bool = True,
        count: bool = True,
    ) -> Pagination:
        """Apply an offset and limit to the query based on the current page and number
        of items per page, returning a :class:`Pagination` object. This is called by
        :meth:`.Query.paginate`, or can be called manually.

        :param query: The query to paginate.
        :param page: The current page, used to calculate the offset. Defaults to the
            ``page`` query arg during a request, or 1 otherwise.
        :param per_page: The maximum number of items on a page, used to calculate the
            offset and limit. Defaults to the ``per_page`` query arg during a request,
            or 20 otherwise.
        :param max_per_page: The maximum allowed value for ``per_page``, to limit a
            user-provided value. Use ``None`` for no limit. Defaults to 100.
        :param error_out: Abort with a ``404 Not Found`` error if no items are returned
            and ``page`` is not 1, or if ``page`` or ``per_page`` is less than 1, or if
            either are not ints.
        :param count: Calculate the total number of values by issuing an extra count
            query. For very complex queries this may be inaccurate or slow, so it can be
            disabled and set manually if necessary.

        .. versionadded:: 3.0

        .. versionchanged:: 3.0
            The ``count`` query is more efficient.

        .. versionchanged:: 3.0
            ``per_page`` cannot be 0.

        .. versionchanged:: 3.0
            ``max_per_page`` defaults to 100.
        """
        page, per_page = cls._prepare_args(
            page=page,
            per_page=per_page,
            max_per_page=max_per_page,
            error_out=error_out,
        )
        items = query.limit(per_page).offset((page - 1) * per_page).all()

        if not items and page != 1 and error_out:
            abort(404)

        if count:
            total = query.options(sa.orm.lazyload("*")).order_by(None).count()
            # Using `.with_entities([sa.func.count()]).scalar()` is an alternative, but
            # is not guaranteed to be correct for many possible queries. If custom
            # counting is needed, it can be disabled here and set manually after.
        else:
            total = None

        return cls(
            query=query,
            page=page,
            per_page=per_page,
            total=total,
            items=items,
        )

    # TODO: apply_to_select, requires access to session

    @property
    def first(self) -> int:
        """The number of the first item on the page, starting from 1, or 0 if there are
        no items.

        .. versionadded:: 3.0
        """
        if len(self.items) == 0:
            return 0

        return (self.page - 1) * self.per_page + 1

    @property
    def last(self) -> int:
        """The number of the last item on the page, starting from 1, inclusive, or 0 if
        there are no items.

        .. versionadded:: 3.0
        """
        first = self.first
        return max(first, first + len(self.items) - 1)

    @property
    def pages(self) -> int:
        """The total number of pages."""
        if self.total == 0 or self.total is None:
            return 0

        return ceil(self.total / self.per_page)

    @property
    def has_prev(self) -> bool:
        """``True`` if this is not the first page."""
        return self.page > 1

    @property
    def prev_num(self) -> int | None:
        """The previous page number, or ``None`` if this is the first page."""
        if not self.has_prev:
            return None

        return self.page - 1

    def prev(self, error_out: bool = False) -> Pagination:
        """Query the :class:`Pagination` object for the previous page."""
        assert self.query is not None
        return self.apply_to_query(
            self.query, page=self.page - 1, per_page=self.per_page, error_out=error_out
        )

    @property
    def has_next(self) -> bool:
        """``True`` if this is not the last page."""
        return self.page < self.pages

    @property
    def next_num(self) -> int | None:
        """The next page number, or ``None`` if this is the last page."""
        if not self.has_next:
            return None

        return self.page + 1

    def next(self, error_out: bool = False) -> Pagination:
        """Query the :class:`Pagination` object for the next page."""
        assert self.query is not None
        return self.apply_to_query(
            self.query, page=self.page + 1, per_page=self.per_page, error_out=error_out
        )

    def iter_pages(
        self,
        *,
        left_edge: int = 2,
        left_current: int = 2,
        right_current: int = 4,
        right_edge: int = 2,
    ) -> t.Iterator[int | None]:
        """Yield page numbers for a pagination widget. Skipped pages between the edges
        and middle are represented by a ``None``.

        For example, if there are 20 pages and the current page is 7, the following
        values are yielded.

        .. code-block:: python

            1, 2, None, 5, 6, 7, 8, 9, 10, 11, None, 19, 20

        :param left_edge: How many pages to show from the first page.
        :param left_current: How many pages to show left of the current page.
        :param right_current: How many pages to show right of the current page.
        :param right_edge: How many pages to show from the last page.

        .. versionchanged:: 3.0
            Improved efficiency of calculating what to yield.

        .. versionchanged:: 3.0
            ``right_current`` boundary is inclusive.

        .. versionchanged:: 3.0
            All parameters are keyword-only.
        """
        pages_end = self.pages + 1

        if pages_end == 1:
            return

        left_end = min(1 + left_edge, pages_end)
        yield from range(1, left_end)

        if left_end == pages_end:
            return

        mid_start = max(left_end, self.page - left_current)
        mid_end = min(self.page + right_current + 1, pages_end)

        if mid_start - left_end > 0:
            yield None

        yield from range(mid_start, mid_end)

        if mid_end == pages_end:
            return

        right_start = max(mid_end, pages_end - right_edge)

        if right_start - mid_end > 0:
            yield None

        yield from range(right_start, pages_end)

    def __iter__(self) -> t.Iterator[t.Any]:
        yield from self.items
