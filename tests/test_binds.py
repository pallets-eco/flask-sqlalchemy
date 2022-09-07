import sqlalchemy as sa

from flask_sqlalchemy import SQLAlchemy


def test_basic_binds(app):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://", "bar": "sqlite://"}
    db = SQLAlchemy(app)

    assert str(db.engine.url) == app.config["SQLALCHEMY_DATABASE_URI"]

    for key in "foo", "bar":
        engine = db.engines[key]
        assert str(engine.url) == app.config["SQLALCHEMY_BINDS"][key]

    class Foo(db.Model):
        __bind_key__ = "foo"
        __table_args__ = {"info": {"bind_key": "foo"}}
        id = db.Column(db.Integer, primary_key=True)

    class Bar(db.Model):
        __bind_key__ = "bar"
        id = db.Column(db.Integer, primary_key=True)

    class Baz(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    db.create_all()

    # do the models have the correct engines?
    assert "foo" in db.metadatas["foo"].tables
    assert "bar" in db.metadatas["bar"].tables
    assert "baz" in db.metadata.tables

    # see the tables created in an engine
    metadata = sa.MetaData()
    metadata.reflect(bind=db.engines["foo"])
    assert len(metadata.tables) == 1
    assert "foo" in metadata.tables

    metadata = sa.MetaData()
    metadata.reflect(bind=db.engines["bar"])
    assert len(metadata.tables) == 1
    assert "bar" in metadata.tables

    metadata = sa.MetaData()
    metadata.reflect(bind=db.engine)
    assert len(metadata.tables) == 1
    assert "baz" in metadata.tables


def test_abstract_binds(app):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://"}
    db = SQLAlchemy(app)

    class AbstractFooBoundModel(db.Model):
        __abstract__ = True
        __bind_key__ = "foo"

    class FooBoundModel(AbstractFooBoundModel):
        id = db.Column(db.Integer, primary_key=True)

    db.create_all()

    # does the model have the correct engine?
    assert "foo_bound_model" in db.metadatas["foo"].tables

    # see the tables created in an engine
    metadata = sa.MetaData()
    metadata.reflect(bind=db.engines["foo"])
    assert len(metadata.tables) == 1
    assert "foo_bound_model" in metadata.tables


def test_polymorphic_bind(app):
    bind_key = "polymorphic_bind_key"
    app.config["SQLALCHEMY_BINDS"] = {bind_key: "sqlite:///:memory"}
    db = SQLAlchemy(app)

    class Base(db.Model):
        __bind_key__ = bind_key
        __tablename__ = "base"
        id = db.Column(db.Integer, primary_key=True)
        p_type = db.Column(db.String(50))
        __mapper_args__ = {"polymorphic_identity": "base", "polymorphic_on": p_type}

    class Child1(Base):
        child_1_data = db.Column(db.String(50))
        __mapper_args__ = {"polymorphic_identity": "child_1"}

    assert Base.metadata.info["bind_key"] == bind_key
    assert Child1.metadata.info["bind_key"] == bind_key


def test_execute_with_binds_arguments(app):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://", "bar": "sqlite://"}
    db = SQLAlchemy(app)
    db.create_all()
    db.session.execute("SELECT true", bind_arguments={"bind": db.engines["foo"]})
