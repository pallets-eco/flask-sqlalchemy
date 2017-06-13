from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

import flask_sqlalchemy as fsa


def test_default_session_scoping(app, db):
    class FOOBar(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    db.create_all()

    with app.test_request_context():
        fb = FOOBar()
        db.session.add(fb)
        assert fb in db.session


def test_session_scoping_changing(app):
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


def test_insert_update_delete(db):
    # Ensure _SignalTrackingMapperExtension doesn't croak when
    # faced with a vanilla SQLAlchemy session.
    #
    # Verifies that "AttributeError: 'SessionMaker' object has no attribute '_model_changes'"
    # is not thrown.
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


def test_listen_to_session_event(db):
    sa.event.listen(db.session, 'after_commit', lambda session: None)


# need to create an instance of the extension so it has the custom session class attached
# ergo the todo model class needs to be implemented here as well
def test_custom_session_class(app):
    tattle = {}

    class CustomSession(fsa.SignallingSession):
        def commit(self):
            super(CustomSession, self).commit()
            tattle['committed'] = True

    db = fsa.SQLAlchemy(app=app, session_options={'class_': CustomSession})

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

    with app.app_context():
        db.create_all()
        db.session.add(Todo(title='test custom session', text='make tattle true on commit'))
        db.session.commit()
        db.drop_all()

    assert tattle['committed']
