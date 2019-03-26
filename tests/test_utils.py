import mock

from flask_sqlalchemy import utils


class TestSQLAlchemyVersion:

    @mock.patch.object(utils, 'sqlalchemy')
    def test_sqlalchemy_version(self, m_sqlalchemy):
        m_sqlalchemy.__version__ = '1.3'

        assert not utils.sqlalchemy_version('<', '1.3')
        assert not utils.sqlalchemy_version('>', '1.3')
        assert utils.sqlalchemy_version('<=', '1.3')
        assert utils.sqlalchemy_version('==', '1.3')
        assert utils.sqlalchemy_version('>=', '1.3')

        m_sqlalchemy.__version__ = '1.2.99'

        assert utils.sqlalchemy_version('<', '1.3')
        assert not utils.sqlalchemy_version('>', '1.3')
        assert utils.sqlalchemy_version('<=', '1.3')
        assert not utils.sqlalchemy_version('==', '1.3')
        assert not utils.sqlalchemy_version('>=', '1.3')
