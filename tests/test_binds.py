from flask_sqlalchemy import get_state
from flask_sqlalchemy import SQLAlchemy


def test_basic_binds(app, db):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://", "bar": "sqlite://"}

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

    # simple way to check if the engines are looked up properly
    assert db.get_engine(app, None) == db.engine
    for key in "foo", "bar":
        engine = db.get_engine(app, key)
        connector = app.extensions["sqlalchemy"].connectors[key]
        assert engine == connector.get_engine()
        assert str(engine.url) == app.config["SQLALCHEMY_BINDS"][key]

    # do the models have the correct engines?
    assert db.metadata.tables["foo"].info["bind_key"] == "foo"
    assert db.metadata.tables["bar"].info["bind_key"] == "bar"
    assert db.metadata.tables["baz"].info.get("bind_key") is None

    # see the tables created in an engine
    metadata = db.MetaData()
    metadata.reflect(bind=db.get_engine(app, "foo"))
    assert len(metadata.tables) == 1
    assert "foo" in metadata.tables

    metadata = db.MetaData()
    metadata.reflect(bind=db.get_engine(app, "bar"))
    assert len(metadata.tables) == 1
    assert "bar" in metadata.tables

    metadata = db.MetaData()
    metadata.reflect(bind=db.get_engine(app))
    assert len(metadata.tables) == 1
    assert "baz" in metadata.tables

    # do the session have the right binds set?
    assert db.get_binds(app) == {
        Foo.__table__: db.get_engine(app, "foo"),
        Bar.__table__: db.get_engine(app, "bar"),
        Baz.__table__: db.get_engine(app, None),
    }


def test_abstract_binds(app, db):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://"}

    class AbstractFooBoundModel(db.Model):
        __abstract__ = True
        __bind_key__ = "foo"

    class FooBoundModel(AbstractFooBoundModel):
        id = db.Column(db.Integer, primary_key=True)

    db.create_all()

    # does the model have the correct engines?
    assert db.metadata.tables["foo_bound_model"].info["bind_key"] == "foo"

    # see the tables created in an engine
    metadata = db.MetaData()
    metadata.reflect(bind=db.get_engine(app, "foo"))
    assert len(metadata.tables) == 1
    assert "foo_bound_model" in metadata.tables


def test_connector_cache(app):
    db = SQLAlchemy()
    db.init_app(app)

    with app.app_context():
        db.get_engine()

    connector = get_state(app).connectors[None]
    assert connector._app is app


def test_polymorphic_bind(app, db):
    bind_key = "polymorphic_bind_key"

    app.config["SQLALCHEMY_BINDS"] = {
        bind_key: "sqlite:///:memory",
    }

    class Base(db.Model):
        __bind_key__ = bind_key

        __tablename__ = "base"

        id = db.Column(db.Integer, primary_key=True)

        p_type = db.Column(db.String(50))

        __mapper_args__ = {"polymorphic_identity": "base", "polymorphic_on": p_type}

    class Child1(Base):

        child_1_data = db.Column(db.String(50))
        __mapper_args__ = {
            "polymorphic_identity": "child_1",
        }

    assert Base.__table__.info["bind_key"] == bind_key
    assert Child1.__table__.info["bind_key"] == bind_key


def test_execute_with_binds_arguments(app, db):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://", "bar": "sqlite://"}
    db.create_all()
    db.session.execute(
        "SELECT true", bind_arguments={"bind": db.get_engine(app, "foo")}
    )


def test_reflect(app, db):
    app.config["SQLALCHEMY_BINDS"] = {"foo": "sqlite://"}
    db.get_engine(app, "foo").execute("CREATE TABLE foo_table (id INTEGER PRIMARY KEY)")
    db.get_engine(app).execute(
        "CREATE TABLE default_bind_table (id INTEGER PRIMARY KEY)"
    )

    db.reflect("foo", app=app)

    assert db.metadata.tables.get("default_bind_table") is None

    foo_table = db.metadata.tables.get("foo_table")
    assert foo_table is not None
    assert foo_table in db.get_tables_for_bind("foo")
    assert foo_table.info.get("bind_key") == "foo"

    db.reflect(app=app)

    default_bind_table = db.metadata.tables.get("default_bind_table")
    assert default_bind_table is not None
    assert default_bind_table in db.get_tables_for_bind(None)
    assert default_bind_table.info.get("bind_key") is None
