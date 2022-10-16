Paging Query Results
====================

If you have a lot of results, you may only want to show a certain number at a time,
allowing the user to click next and previous links to see pages of data. This is
sometimes called *pagination*, and uses the verb *paginate*.

Call :meth:`.SQLAlchemy.paginate` on a select statement to get a :class:`.Pagination`
object.

During a request, this will take ``page`` and ``per_page`` arguments from the query
string ``request.args``. Pass ``max_per_page`` to prevent users from requesting too many
results on a single page. If not given, the default values will be page 1 with 20 items
per page.

.. code-block:: python

    page = db.paginate(db.select(User).order_by(User.join_date))
    return render_template("user/list.html", page=page)


Showing the Items
-----------------

The :class:`.Pagination` object's :attr:`.Pagination.items` attribute is the list of
items for the current page. The object can also be iterated over directly.

.. code-block:: jinja

    <ul>
      {% for user in page %}
        <li>{{ user.username }}
      {% endfor %}
    </ul>


Page Selection Widget
---------------------

The :class:`.Pagination` object has attributes that can be used to create a page
selection widget by iterating over page numbers and checking the current page.
:meth:`~.Pagination.iter_pages` will produce up to three groups of numbers, separated by
``None``. It defaults to showing 2 page numbers at either edge, 2 numbers before the
current, the current, and 4 numbers after the current. For example, if there are 20
pages and the current page is 7, the following values are yielded.

.. code-block:: python

    users.iter_pages()
    [1, 2, None, 5, 6, 7, 8, 9, 10, 11, None, 19, 20]

You can use the :attr:`~.Pagination.total` attribute to show the total number of
results, and :attr:`~.Pagination.first` and :attr:`~.Pagination.last` to show the
range of items on the current page.

The following Jinja macro renders a simple pagination widget.

.. code-block:: jinja

    {% macro render_pagination(pagination, endpoint) %}
      <div class=page-items>
        {{ pagination.first }} - {{ pagination.last }} of {{ pagination.total }}
      </div>
      <div class=pagination>
        {% for page in pagination.iter_pages() %}
          {% if page %}
            {% if page != pagination.page %}
              <a href="{{ url_for(endpoint, page=page) }}">{{ page }}</a>
            {% else %}
              <strong>{{ page }}</strong>
            {% endif %}
          {% else %}
            <span class=ellipsis>…</span>
          {% endif %}
        {% endfor %}
      </div>
    {% endmacro %}
