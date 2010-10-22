from __future__ import with_statement

import unittest
from datetime import datetime
import flask
from flaskext import sqlalchemy


def make_todo_model(db):
    class Todo(db.Model):
        __tablename__ = 'todos'
        id = db.Column('todo_id', db.Integer, primary_key=True)
        title = db.Column(db.String(60))
        text = db.Column(db.String)
        done = db.Column(db.Boolean)
        pub_date = db.Column(db.DateTime)

        def __init__(self, title, text):
            self.title = title
            self.text = text
            self.done = False
            self.pub_date = datetime.utcnow()
    return Todo


class BasicAppTestCase(unittest.TestCase):

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        app.config['TESTING'] = True
        db = sqlalchemy.SQLAlchemy(app)
        self.Todo = make_todo_model(db)

        @app.route('/')
        def index():
            return '\n'.join(x.title for x in self.Todo.query.all())

        @app.route('/add', methods=['POST'])
        def add():
            form = flask.request.form
            todo = self.Todo(form['title'], form['text'])
            db.session.add(todo)
            db.session.commit()
            return 'added'

        db.create_all()

        self.app = app
        self.db = db

    def tearDown(self):
        self.db.drop_all()

    def test_basic_insert(self):
        c = self.app.test_client()
        c.post('/add', data=dict(title='First Item', text='The text'))
        c.post('/add', data=dict(title='2nd Item', text='The text'))
        rv = c.get('/')
        assert rv.data == 'First Item\n2nd Item'

    def test_query_recording(self):
        with self.app.test_request_context():
            todo = self.Todo('Test 1', 'test')
            self.db.session.add(todo)
            self.db.session.commit()

            queries = sqlalchemy.get_debug_queries()
            self.assertEqual(len(queries), 1)
            query = queries[0]
            self.assert_('insert into' in query.statement.lower())
            self.assertEqual(query.parameters[0], 'Test 1')
            self.assertEqual(query.parameters[1], 'test')
            self.assert_('test_sqlalchemy.py' in query.context)
            self.assert_('test_query_recording' in query.context)

    def test_helper_api(self):
        self.assertEqual(self.db.metadata, self.db.Model.metadata)


class TestQueryProperty(unittest.TestCase):

    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        self.app.config['TESTING'] = True

    def test_no_app_bound(self):
        db = sqlalchemy.SQLAlchemy()
        db.init_app(self.app)
        Todo = make_todo_model(db)

        # If no app is bound to the SQLAlchemy instance, a
        # request context is required to access Model.query.
        self.assertRaises(RuntimeError, getattr, Todo, 'query')
        with self.app.test_request_context():
            db.create_all()
            todo = Todo('Test', 'test')
            db.session.add(todo)
            db.session.commit()
            self.assertEqual(len(Todo.query.all()), 1)

    def test_app_bound(self):
        db = sqlalchemy.SQLAlchemy(self.app)
        Todo = make_todo_model(db)
        db.create_all()

        # If an app was passed to the SQLAlchemy constructor,
        # the query property is always available.
        todo = Todo('Test', 'test')
        db.session.add(todo)
        db.session.commit()
        self.assertEqual(len(Todo.query.all()), 1)


class SignallingTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app = flask.Flask(__name__)
        app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        app.config['TESTING'] = True
        self.db = sqlalchemy.SQLAlchemy(app)
        self.Todo = make_todo_model(self.db)
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def test_model_signals(self):
        recorded = []
        def committed(sender, changes):
            self.assert_(isinstance(changes, list))
            recorded.extend(changes)
        with sqlalchemy.models_committed.connected_to(committed,
                                                      sender=self.app):
            todo = self.Todo('Awesome', 'the text')
            self.db.session.add(todo)
            self.assertEqual(len(recorded), 0)
            self.db.session.commit()
            self.assertEqual(len(recorded), 1)
            self.assertEqual(recorded[0][0], todo)
            self.assertEqual(recorded[0][1], 'insert')
            del recorded[:]
            todo.text = 'aha'
            self.db.session.commit()
            self.assertEqual(len(recorded), 1)
            self.assertEqual(recorded[0][0], todo)
            self.assertEqual(recorded[0][1], 'update')
            del recorded[:]
            self.db.session.delete(todo)
            self.db.session.commit()
            self.assertEqual(len(recorded), 1)
            self.assertEqual(recorded[0][0], todo)
            self.assertEqual(recorded[0][1], 'delete')


class HelperTestCase(unittest.TestCase):

    def test_default_table_name(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        db = sqlalchemy.SQLAlchemy(app)

        class FOOBar(db.Model):
            id = db.Column(db.Integer, primary_key=True)
        class BazBar(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        self.assertEqual(FOOBar.__tablename__, 'foo_bar')
        self.assertEqual(BazBar.__tablename__, 'baz_bar')


class PaginationTestCase(unittest.TestCase):

    def test_basic_pagination(self):
        p = sqlalchemy.Pagination(None, 1, 20, 500, [])
        self.assertEqual(p.page, 1)
        self.assertFalse(p.has_prev)
        self.assert_(p.has_next)
        self.assertEqual(p.total, 500)
        self.assertEqual(p.pages, 25)
        self.assertEqual(p.next_num, 2)
        self.assertEqual(list(p.iter_pages()),
                         [1, 2, 3, 4, 5, None, 24, 25])
        p.page = 10
        self.assertEqual(list(p.iter_pages()),
                         [1, 2, None, 8, 9, 10, 11, 12, 13, 14, None, 24, 25])


if __name__ == '__main__':
    unittest.main()
