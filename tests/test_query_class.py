import pytest

from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy.query import Query


@pytest.mark.usefixtures("app_ctx")
def test_default_query_class(db):
    class Parent(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        children = db.relationship("Child", backref="parent", lazy="dynamic")

    class Child(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        parent_id = db.Column(db.Integer, db.ForeignKey("parent.id"))

    p = Parent()
    c = Child()
    c.parent = p

    assert type(Parent.query) == Query
    assert type(Child.query) == Query
    assert isinstance(p.children, Query)
    assert isinstance(db.session.query(Parent), Query)


@pytest.mark.usefixtures("app_ctx")
def test_custom_query_class(app):
    class CustomQueryClass(Query):
        pass

    db = SQLAlchemy(app, query_class=CustomQueryClass)

    class Parent(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        children = db.relationship("Child", backref="parent", lazy="dynamic")

    class Child(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        parent_id = db.Column(db.Integer, db.ForeignKey("parent.id"))

    p = Parent()
    c = Child()
    c.parent = p

    assert type(Parent.query) == CustomQueryClass
    assert type(Child.query) == CustomQueryClass
    assert isinstance(p.children, CustomQueryClass)
    assert db.Query == CustomQueryClass
    assert db.Model.query_class == CustomQueryClass
    assert isinstance(db.session.query(Parent), CustomQueryClass)


@pytest.mark.usefixtures("app_ctx")
def test_dont_override_model_default(app):
    class CustomQueryClass(Query):
        pass

    db = SQLAlchemy(app, query_class=CustomQueryClass)

    class SomeModel(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        query_class = Query

    assert type(SomeModel.query) == Query
