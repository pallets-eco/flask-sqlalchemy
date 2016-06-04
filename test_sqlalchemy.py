#!/usr/bin/env python
from __future__ import with_statement

import unittest
from datetime import datetime

import flask
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import sessionmaker

import flask_sqlalchemy as fsa


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
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app)
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
        self.assertEqual(rv.data, b'First Item\n2nd Item')

    def test_query_recording(self):
        with self.app.test_request_context():
            todo = self.Todo('Test 1', 'test')
            self.db.session.add(todo)
            self.db.session.commit()

            queries = fsa.get_debug_queries()
            self.assertEqual(len(queries), 1)
            query = queries[0]
            self.assertTrue('insert into' in query.statement.lower())
            self.assertEqual(query.parameters[0], 'Test 1')
            self.assertEqual(query.parameters[1], 'test')
            self.assertTrue('test_sqlalchemy.py' in query.context)
            self.assertTrue('test_query_recording' in query.context)

    def test_helper_api(self):
        self.assertEqual(self.db.metadata, self.db.Model.metadata)


class MetaDataTestCase(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['TESTING'] = True

    def test_default_metadata(self):
        db = fsa.SQLAlchemy(self.app, metadata=None)
        self.db = db

        class One(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            myindex = db.Column(db.Integer, index=True)

        class Two(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            one_id = db.Column(db.Integer, db.ForeignKey(One.id))
            myunique = db.Column(db.Integer, unique=True)

        self.assertTrue(One.metadata.__class__ is sa.MetaData)
        self.assertTrue(Two.metadata.__class__ is sa.MetaData)

        self.assertEqual(One.__table__.schema, None)
        self.assertEqual(Two.__table__.schema, None)

    def test_custom_metadata(self):
        class CustomMetaData(sa.MetaData):
            pass

        custom_metadata = CustomMetaData(schema="test_schema")
        db = fsa.SQLAlchemy(self.app, metadata=custom_metadata)
        self.db = db

        class One(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            myindex = db.Column(db.Integer, index=True)

        class Two(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            one_id = db.Column(db.Integer, db.ForeignKey(One.id))
            myunique = db.Column(db.Integer, unique=True)

        self.assertTrue(One.metadata is custom_metadata)
        self.assertTrue(Two.metadata is custom_metadata)

        self.assertFalse(One.metadata.__class__ is sa.MetaData)
        self.assertTrue(One.metadata.__class__ is CustomMetaData)

        self.assertFalse(Two.metadata.__class__ is sa.MetaData)
        self.assertTrue(Two.metadata.__class__ is CustomMetaData)

        self.assertEqual(One.__table__.schema, "test_schema")
        self.assertEqual(Two.__table__.schema, "test_schema")


class TestQueryProperty(unittest.TestCase):
    def setUp(self):
        self.app = flask.Flask(__name__)
        self.app.config['TESTING'] = True

    def test_no_app_bound(self):
        db = fsa.SQLAlchemy()
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
        db = fsa.SQLAlchemy(self.app)
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
        app.config['TESTING'] = True
        self.db = fsa.SQLAlchemy(app)
        self.Todo = make_todo_model(self.db)
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def test_before_committed(self):
        class Namespace(object):
            is_received = False

        def before_committed(sender, changes):
            Namespace.is_received = True

        fsa.before_models_committed.connect(before_committed)
        todo = self.Todo('Awesome', 'the text')
        self.db.session.add(todo)
        self.db.session.commit()
        self.assertTrue(Namespace.is_received)
        fsa.before_models_committed.disconnect(before_committed)

    def test_model_signals(self):
        recorded = []

        def committed(sender, changes):
            self.assertTrue(isinstance(changes, list))
            recorded.extend(changes)

        fsa.models_committed.connect(committed)
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
        fsa.models_committed.disconnect(committed)


class TablenameTestCase(unittest.TestCase):
    def test_name(self):
        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class FOOBar(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        class BazBar(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        class Ham(db.Model):
            __tablename__ = 'spam'
            id = db.Column(db.Integer, primary_key=True)

        self.assertEqual(FOOBar.__tablename__, 'foo_bar')
        self.assertEqual(BazBar.__tablename__, 'baz_bar')
        self.assertEqual(Ham.__tablename__, 'spam')

    def test_single_name(self):
        """Single table inheritance should not set a new name."""

        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Duck(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        class Mallard(Duck):
            pass

        self.assertEqual(Mallard.__tablename__, 'duck')

    def test_joined_name(self):
        """Model has a separate primary key; it should set a new name."""

        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Duck(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        class Donald(Duck):
            id = db.Column(db.Integer, db.ForeignKey(Duck.id), primary_key=True)

        self.assertEqual(Donald.__tablename__, 'donald')

    def test_mixin_name(self):
        """Primary key provided by mixin should still allow model to set tablename."""

        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Base(object):
            id = db.Column(db.Integer, primary_key=True)

        class Duck(Base, db.Model):
            pass

        self.assertFalse(hasattr(Base, '__tablename__'))
        self.assertEqual(Duck.__tablename__, 'duck')

    def test_abstract_name(self):
        """Abstract model should not set a name.  Subclass should set a name."""

        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Base(db.Model):
            __abstract__ = True
            id = db.Column(db.Integer, primary_key=True)

        class Duck(Base):
            pass

        self.assertFalse(hasattr(Base, '__tablename__'))
        self.assertEqual(Duck.__tablename__, 'duck')

    def test_complex_inheritance(self):
        """Joined table inheritance, but the new primary key is provided by a mixin, not directly on the class."""

        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Duck(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        class IdMixin(object):
            @declared_attr
            def id(cls):
                return db.Column(db.Integer, db.ForeignKey(Duck.id), primary_key=True)

        class RubberDuck(IdMixin, Duck):
            pass

        self.assertEqual(RubberDuck.__tablename__, 'rubber_duck')


class PaginationTestCase(unittest.TestCase):
    def test_basic_pagination(self):
        p = fsa.Pagination(None, 1, 20, 500, [])
        self.assertEqual(p.page, 1)
        self.assertFalse(p.has_prev)
        self.assertTrue(p.has_next)
        self.assertEqual(p.total, 500)
        self.assertEqual(p.pages, 25)
        self.assertEqual(p.next_num, 2)
        self.assertEqual(list(p.iter_pages()),
                         [1, 2, 3, 4, 5, None, 24, 25])
        p.page = 10
        self.assertEqual(list(p.iter_pages()),
                         [1, 2, None, 8, 9, 10, 11, 12, 13, 14, None, 24, 25])

    def test_pagination_pages_when_0_items_per_page(self):
        p = fsa.Pagination(None, 1, 0, 500, [])
        self.assertEqual(p.pages, 0)

    def test_query_paginate(self):
        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)
        Todo = make_todo_model(db)
        db.create_all()

        with app.app_context():
            db.session.add_all([Todo('', '') for _ in range(100)])
            db.session.commit()

        @app.route('/')
        def index():
            p = Todo.query.paginate()
            return '{0} items retrieved'.format(len(p.items))

        c = app.test_client()
        # request default
        r = c.get('/')
        self.assertEqual(r.status_code, 200)
        # request args
        r = c.get('/?per_page=10')
        self.assertEqual(r.data.decode('utf8'), '10 items retrieved')

        with app.app_context():
            # query default
            p = Todo.query.paginate()
            self.assertEqual(p.total, 100)


class BindsTestCase(unittest.TestCase):
    def test_basic_binds(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_BINDS'] = {
            'foo': 'sqlite://',
            'bar': 'sqlite://'
        }
        db = fsa.SQLAlchemy(app)

        class Foo(db.Model):
            __bind_key__ = 'foo'
            __table_args__ = {"info": {"bind_key": "foo"}}
            id = db.Column(db.Integer, primary_key=True)

        class Bar(db.Model):
            __bind_key__ = 'bar'
            id = db.Column(db.Integer, primary_key=True)

        class Baz(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        db.create_all()

        # simple way to check if the engines are looked up properly
        self.assertEqual(db.get_engine(app, None), db.engine)
        for key in 'foo', 'bar':
            engine = db.get_engine(app, key)
            connector = app.extensions['sqlalchemy'].connectors[key]
            self.assertEqual(engine, connector.get_engine())
            self.assertEqual(str(engine.url),
                             app.config['SQLALCHEMY_BINDS'][key])

        # do the models have the correct engines?
        self.assertEqual(db.metadata.tables['foo'].info['bind_key'], 'foo')
        self.assertEqual(db.metadata.tables['bar'].info['bind_key'], 'bar')
        self.assertEqual(db.metadata.tables['baz'].info.get('bind_key'), None)

        # see the tables created in an engine
        metadata = db.MetaData()
        metadata.reflect(bind=db.get_engine(app, 'foo'))
        self.assertEqual(len(metadata.tables), 1)
        self.assertTrue('foo' in metadata.tables)

        metadata = db.MetaData()
        metadata.reflect(bind=db.get_engine(app, 'bar'))
        self.assertEqual(len(metadata.tables), 1)
        self.assertTrue('bar' in metadata.tables)

        metadata = db.MetaData()
        metadata.reflect(bind=db.get_engine(app))
        self.assertEqual(len(metadata.tables), 1)
        self.assertTrue('baz' in metadata.tables)

        # do the session have the right binds set?
        self.assertEqual(db.get_binds(app), {
            Foo.__table__: db.get_engine(app, 'foo'),
            Bar.__table__: db.get_engine(app, 'bar'),
            Baz.__table__: db.get_engine(app, None)
        })

    def test_abstract_binds(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_BINDS'] = {
            'foo': 'sqlite://'
        }
        db = fsa.SQLAlchemy(app)

        class AbstractFooBoundModel(db.Model):
            __abstract__ = True
            __bind_key__ = 'foo'

        class FooBoundModel(AbstractFooBoundModel):
            id = db.Column(db.Integer, primary_key=True)

        db.create_all()

        # does the model have the correct engines?
        self.assertEqual(db.metadata.tables['foo_bound_model'].info['bind_key'], 'foo')

        # see the tables created in an engine
        metadata = db.MetaData()
        metadata.reflect(bind=db.get_engine(app, 'foo'))
        self.assertEqual(len(metadata.tables), 1)
        self.assertTrue('foo_bound_model' in metadata.tables)


class DefaultQueryClassTestCase(unittest.TestCase):
    def test_default_query_class(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app)

        class Parent(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            children = db.relationship("Child", backref="parent", lazy='dynamic')

        class Child(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))

        p = Parent()
        c = Child()
        c.parent = p

        self.assertEqual(type(Parent.query), fsa.BaseQuery)
        self.assertEqual(type(Child.query), fsa.BaseQuery)
        self.assertTrue(isinstance(p.children, fsa.BaseQuery))
        self.assertTrue(isinstance(db.session.query(Parent), fsa.BaseQuery))


class CustomQueryClassTestCase(unittest.TestCase):
    def test_custom_query_class(self):
        class CustomQueryClass(fsa.BaseQuery):
            pass

        class MyModelClass(object):
            pass

        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app, query_class=CustomQueryClass,
                            model_class=MyModelClass)

        class Parent(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            children = db.relationship("Child", backref="parent", lazy='dynamic')

        class Child(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'))

        p = Parent()
        c = Child()
        c.parent = p

        self.assertEqual(type(Parent.query), CustomQueryClass)
        self.assertEqual(type(Child.query), CustomQueryClass)
        self.assertTrue(isinstance(p.children, CustomQueryClass))
        self.assertEqual(db.Query, CustomQueryClass)
        self.assertEqual(db.Model.query_class, CustomQueryClass)
        self.assertTrue(isinstance(db.session.query(Parent), CustomQueryClass))

    def test_dont_override_model_default(self):
        class CustomQueryClass(fsa.BaseQuery):
            pass

        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app, query_class=CustomQueryClass)

        class SomeModel(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            query_class = fsa.BaseQuery

        self.assertEqual(type(SomeModel.query), fsa.BaseQuery)


class CustomModelClassTestCase(unittest.TestCase):
    def test_custom_query_class(self):
        class CustomModelClass(fsa.Model):
            pass

        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app, model_class=CustomModelClass)

        class SomeModel(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        self.assertTrue(isinstance(SomeModel(), CustomModelClass))


class SQLAlchemyIncludesTestCase(unittest.TestCase):
    def test(self):
        """Various SQLAlchemy objects are exposed as attributes.
        """
        db = fsa.SQLAlchemy()

        self.assertTrue(db.Column == sa.Column)

        # The Query object we expose is actually our own subclass.
        from flask_sqlalchemy import BaseQuery
        self.assertTrue(db.Query == BaseQuery)


class RegressionTestCase(unittest.TestCase):
    def test_joined_inheritance(self):
        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Base(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            type = db.Column(db.Unicode(20))
            __mapper_args__ = {'polymorphic_on': type}

        class SubBase(Base):
            id = db.Column(db.Integer, db.ForeignKey('base.id'),
                           primary_key=True)
            __mapper_args__ = {'polymorphic_identity': 'sub'}

        self.assertEqual(Base.__tablename__, 'base')
        self.assertEqual(SubBase.__tablename__, 'sub_base')
        db.create_all()

    def test_single_table_inheritance(self):
        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Base(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            type = db.Column(db.Unicode(20))
            __mapper_args__ = {'polymorphic_on': type}

        class SubBase(Base):
            __mapper_args__ = {'polymorphic_identity': 'sub'}

        self.assertEqual(Base.__tablename__, 'base')
        self.assertEqual(SubBase.__tablename__, 'base')
        db.create_all()

    def test_joined_inheritance_relation(self):
        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)

        class Relation(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            base_id = db.Column(db.Integer, db.ForeignKey('base.id'))
            name = db.Column(db.Unicode(20))

            def __init__(self, name):
                self.name = name

        class Base(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            type = db.Column(db.Unicode(20))
            __mapper_args__ = {'polymorphic_on': type}

        class SubBase(Base):
            id = db.Column(db.Integer, db.ForeignKey('base.id'),
                           primary_key=True)
            __mapper_args__ = {'polymorphic_identity': u'sub'}
            relations = db.relationship(Relation)

        db.create_all()

        base = SubBase()
        base.relations = [Relation(name=u'foo')]
        db.session.add(base)
        db.session.commit()

        base = base.query.one()

    def test_connection_binds(self):
        app = flask.Flask(__name__)
        db = fsa.SQLAlchemy(app)
        assert db.session.connection()


class SessionScopingTestCase(unittest.TestCase):
    def test_default_session_scoping(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app)

        class FOOBar(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        db.create_all()

        with app.test_request_context():
            fb = FOOBar()
            db.session.add(fb)
            assert fb in db.session

    def test_session_scoping_changing(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True

        def scopefunc():
            return id(dict())

        db = fsa.SQLAlchemy(app, session_options=dict(scopefunc=scopefunc))

        class FOOBar(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        db.create_all()

        with app.test_request_context():
            fb = FOOBar()
            db.session.add(fb)
            assert fb not in db.session  # because a new scope is generated on each call


class CommitOnTeardownTestCase(unittest.TestCase):
    def setUp(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
        db = fsa.SQLAlchemy(app)
        Todo = make_todo_model(db)
        db.create_all()

        @app.route('/')
        def index():
            return '\n'.join(x.title for x in Todo.query.all())

        @app.route('/create', methods=['POST'])
        def create():
            db.session.add(Todo('Test one', 'test'))
            if flask.request.form.get('fail'):
                raise RuntimeError("Failing as requested")
            return 'ok'

        self.client = app.test_client()

    def test_commit_on_success(self):
        resp = self.client.post('/create')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.client.get('/').data, b'Test one')

    def test_roll_back_on_failure(self):
        resp = self.client.post('/create', data={'fail': 'on'})
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(self.client.get('/').data, b'')


class StandardSessionTestCase(unittest.TestCase):
    def test_insert_update_delete(self):
        # Ensure _SignalTrackingMapperExtension doesn't croak when
        # faced with a vanilla SQLAlchemy session.
        #
        # Verifies that "AttributeError: 'SessionMaker' object has no attribute '_model_changes'"
        # is not thrown.
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app)
        Session = sessionmaker(bind=db.engine)

        class QazWsx(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            x = db.Column(db.String, default='')

        db.create_all()
        session = Session()
        session.add(QazWsx())
        session.flush()  # issues an INSERT.
        session.expunge_all()
        qaz_wsx = session.query(QazWsx).first()
        assert qaz_wsx.x == ''
        qaz_wsx.x = 'test'
        session.flush()  # issues an UPDATE.
        session.expunge_all()
        qaz_wsx = session.query(QazWsx).first()
        assert qaz_wsx.x == 'test'
        session.delete(qaz_wsx)  # issues a DELETE.
        assert session.query(QazWsx).first() is None

    def test_listen_to_session_event(self):
        app = flask.Flask(__name__)
        app.config['TESTING'] = True
        db = fsa.SQLAlchemy(app)
        sa.event.listen(db.session, 'after_commit', lambda session: None)

class RawSQLADeclarativeBaseTestCase(unittest.TestCase):

    def sqla_raw_declarative_base(self):
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, String, Integer, ForeignKey
        from sqlalchemy.orm import relationship

        Base = declarative_base()

        class Bar(Base):
            __tablename__ = 'bar'
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey('foo.id'))


        class Foo(Base):
            __tablename__ = 'foo'
            id = Column(Integer, primary_key=True)
            string = Column(String(255))
            children = relationship("Bar", lazy='dynamic')


        return Base, Foo, Bar

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        app.config['TESTING'] = True
        self.Base, self.Foo, self.Bar = self.sqla_raw_declarative_base()
        db = fsa.SQLAlchemy(app)
        
        
        db.register_base(self.Base)
        db.create_all()

        self.db = db
        self.app = app
        
    def tearDown(self):
        self.db.drop_all()


    def test_register_base_success(self):

        self.assertTrue(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'foo'))
        self.assertTrue(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'bar'))
        self.assertFalse(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'faketable'))

    def test_drop_all(self):
        # Make sure the tables were originally created so we can compare
        # the fact that they have been dropped.
        self.assertTrue(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'foo'))
        self.assertTrue(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'bar'))

        self.db.drop_all()
        self.assertFalse(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'foo'))
        self.assertFalse(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 'bar'))

        
    def test_query_insert(self):

        self.assertEqual(len(self.Foo.query.all()), 0)

        foo = self.Foo(string='Foo')

        self.db.session.add(foo)
        self.db.session.commit()

        self.assertEqual(len(self.db.session.query(self.Foo).all()), 1)
        self.assertEqual(self.db.session.query(self.Foo).count(), 1)

        first_foo = self.db.session.query(self.Foo).first()
        self.assertEqual(first_foo.string, 'Foo')

    def test_query_property(self):
            
        self.assertEqual(len(self.Foo.query.all()), 0)
        foo = self.Foo(string='Foo')

        self.db.session.add(foo)
        self.db.session.commit()

        self.assertEqual(len(self.Foo.query.all()), 1)
        self.assertEqual(self.Foo.query.count(), 1)

        first_foo = self.Foo.query.first()
        self.assertEqual(first_foo.string, 'Foo')
        

    def test_default_query_class(self):
        # Also test children.
        p = self.Foo()
        c = self.Bar()
        c.parent = p

        self.assertEqual(type(self.Foo.query), fsa.BaseQuery)
        self.assertEqual(type(self.Bar.query), fsa.BaseQuery)

        # Unable to override SQLA's relationship constructor to use our 
        # own query class for relationships, since we cannot inspect the 
        # relationship. If we can get enough info about how the original
        # relationship property was constructed, we could reconstruct using
        # a wrapped relationship property. Disabling this test for now.

        # self.assertTrue(isinstance(p.children, sqlalchemy.BaseQuery))



class RawSQLAMultipleDeclarativeBaseTestCase(unittest.TestCase):

    def sqla_raw_declarative_base(self):
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy import Column, String, Integer, ForeignKey
        from sqlalchemy.orm import relationship

        models = dict()

        Base_A = declarative_base()
        Base_B = declarative_base()
        Base_C = declarative_base()

        class Bar_A(Base_A):
            __tablename__ = 'bar_A'
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey('foo_A.id'))


        class Foo_A(Base_A):
            __tablename__ = 'foo_A'
            id = Column(Integer, primary_key=True)
            string = Column(String(255))
            children = relationship("Bar_A", lazy='dynamic')

        models['A'] = dict(
            Foo=Foo_A,
            Bar=Bar_A,
            Base=Base_A
        )

        class Bar_B(Base_B):
            __tablename__ = 'bar_B'
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey('foo_B.id'))


        class Foo_B(Base_B):
            __tablename__ = 'foo_B'
            id = Column(Integer, primary_key=True)
            string = Column(String(255))
            children = relationship("Bar_B", lazy='dynamic')

        models['B'] = dict(
            Foo=Foo_B,
            Bar=Bar_B,
            Base=Base_B
        )

        class Bar_C(Base_C):
            __tablename__ = 'bar_C'
            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey('foo_C.id'))


        class Foo_C(Base_C):
            __tablename__ = 'foo_C'
            id = Column(Integer, primary_key=True)
            string = Column(String(255))
            children = relationship("Bar_C", lazy='dynamic')

        models['C'] = dict(
            Foo=Foo_C,
            Bar=Bar_C,
            Base=Base_C
        )
        
        
        return models

    def setUp(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_ENGINE'] = 'sqlite://'
        app.config['TESTING'] = True
        self.model_suffixes = ['A','B','C']

        self.Models = self.sqla_raw_declarative_base()
        db = fsa.SQLAlchemy(app)
        
        for base_group in self.Models.values():
            db.register_base(base_group['Base'])
        db.create_all()

        self.db = db
        self.app = app

        
    def tearDown(self):
        self.db.drop_all()

    def test_register_base_success(self):
        for suffix in self.model_suffixes:
            self.assertTrue(self.db.engine.dialect.has_table(
                self.db.engine.connect(), 
                'foo_{0}'.format(suffix)))
            self.assertTrue(self.db.engine.dialect.has_table(
                self.db.engine.connect(), 
                'bar_{0}'.format(suffix)))

        self.assertFalse(self.db.engine.dialect.has_table(
            self.db.engine.connect(), 
            'faketable'))

        
    def test_query_insert(self):
        for suffix in self.model_suffixes:
            self.assertEqual(len(self.db.session.query(
                self.Models[suffix]['Foo']).all()), 0)

            foo = self.Models[suffix]['Foo'](string='Foo_{0}'.format(suffix))
            self.db.session.add(foo)
            self.db.session.commit()

            self.assertEqual(len(self.db.session.query(
                self.Models[suffix]['Foo']).all()), 1)
            self.assertEqual(self.db.session.query(
                self.Models[suffix]['Foo']).count(), 1)

            first_foo = self.db.session.query(
                self.Models[suffix]['Foo']).first()
            self.assertEqual(first_foo.string, 'Foo_{0}'.format(suffix))


    def test_query_property(self):
        for suffix in self.model_suffixes:
            self.assertEqual(len(self.Models[suffix]['Foo'].query.all()), 0)

            foo = self.Models[suffix]['Foo'](string='Foo')
            self.db.session.add(foo)
            self.db.session.commit()

            self.assertEqual(len(self.Models[suffix]['Foo'].query.all()), 1)
            self.assertEqual(self.Models[suffix]['Foo'].query.count(), 1)

            first_foo = self.Models[suffix]['Foo'].query.first()
            self.assertEqual(first_foo.string, 'Foo')
        

    def test_default_query_class(self):
        # Also test children.
        for suffix in self.model_suffixes:
            p = self.Models[suffix]['Foo']()
            c = self.Models[suffix]['Bar']()
            c.parent = p

            self.assertEqual(
                type(self.Models[suffix]['Foo'].query), 
                fsa.BaseQuery)
            self.assertEqual(
                type(self.Models[suffix]['Bar'].query), 
                fsa.BaseQuery)

            # Unable to override SQLA's relationship constructor to use our 
            # own query class for relationships, since we cannot inspect the 
            # relationship. If we can get enough info about how the original
            # relationship property was constructed, we could reconstruct using
            # a wrapped relationship property. Disabling this test for now.

            # self.assertTrue(isinstance(p.children, sqlalchemy.BaseQuery))

    def test_drop_all(self):
        # Make sure they exist before drop, so we can compare the result.
        for suffix in self.model_suffixes:
            self.assertTrue(self.db.engine.dialect.has_table(
                self.db.engine.connect(), 'foo_{0}'.format(suffix)))
            self.assertTrue(self.db.engine.dialect.has_table(
                self.db.engine.connect(), 'bar_{0}'.format(suffix)))

        self.db.drop_all()
        for suffix in self.model_suffixes:
            self.assertFalse(self.db.engine.dialect.has_table(
                self.db.engine.connect(), 'foo_{0}'.format(suffix)))
            self.assertFalse(self.db.engine.dialect.has_table(
                self.db.engine.connect(), 'bar_{0}'.format(suffix)))

def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(RegressionTestCase))
    suite.addTest(unittest.makeSuite(BasicAppTestCase))
    suite.addTest(unittest.makeSuite(SQLAlchemyIncludesTestCase))
    suite.addTest(unittest.makeSuite(MetaDataTestCase))
    suite.addTest(unittest.makeSuite(TestQueryProperty))
    suite.addTest(unittest.makeSuite(DefaultQueryClassTestCase))
    suite.addTest(unittest.makeSuite(CustomQueryClassTestCase))
    suite.addTest(unittest.makeSuite(TablenameTestCase))
    suite.addTest(unittest.makeSuite(PaginationTestCase))
    suite.addTest(unittest.makeSuite(BindsTestCase))
    suite.addTest(unittest.makeSuite(StandardSessionTestCase))
    suite.addTest(unittest.makeSuite(SessionScopingTestCase))
    suite.addTest(unittest.makeSuite(CommitOnTeardownTestCase))
    suite.addTest(unittest.makeSuite(CustomModelClassTestCase))
    suite.addTest(unittest.makeSuite(RawSQLADeclarativeBaseTestCase))
    suite.addTest(unittest.makeSuite(RawSQLAMultipleDeclarativeBaseTestCase))

    if flask.signals_available:
        suite.addTest(unittest.makeSuite(SignallingTestCase))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
