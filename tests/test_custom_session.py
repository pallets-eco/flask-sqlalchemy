import flask_sqlalchemy as fsa
from datetime import datetime


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
