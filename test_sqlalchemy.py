import unittest
from flaskext import sqlalchemy


class PaginationTestCase(unittest.TestCase):

    def test_basic_pagination(self):
        p = sqlalchemy.Pagination(None, 1, 20, 500, [])
        assert p.page == 1
        assert not p.has_prev
        assert p.has_next
        assert p.total == 500
        assert p.pages == 25
        assert p.next_num == 2
        assert list(p.iter_numbers()) == [1, 2, 3, 4, 5, None, 24, 25]
        p.page = 10
        assert list(p.iter_numbers()) == [1, 2, None, 8, 9, 10, 11,
                                          12, 13, 14, None, 24, 25]


if __name__ == '__main__':
    unittest.main()
