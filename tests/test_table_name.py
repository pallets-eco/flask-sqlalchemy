from sqlalchemy.ext.declarative import declared_attr


def test_name(db):
    class FOOBar(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class BazBar(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class Ham(db.Model):
        __tablename__ = 'spam'
        id = db.Column(db.Integer, primary_key=True)

    assert FOOBar.__tablename__ == 'foo_bar'
    assert BazBar.__tablename__ == 'baz_bar'
    assert Ham.__tablename__ == 'spam'


def test_single_name(db):
    """Single table inheritance should not set a new name."""
    class Duck(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class Mallard(Duck):
        pass

    assert Mallard.__tablename__ == 'duck'


def test_joined_name(db):
    """Model has a separate primary key; it should set a new name."""
    class Duck(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class Donald(Duck):
        id = db.Column(db.Integer, db.ForeignKey(Duck.id), primary_key=True)

    assert Donald.__tablename__ == 'donald'


def test_mixin_name(db):
    """Primary key provided by mixin should still allow model to set tablename."""
    class Base(object):
        id = db.Column(db.Integer, primary_key=True)

    class Duck(Base, db.Model):
        pass

    assert not hasattr(Base, '__tablename__')
    assert Duck.__tablename__ == 'duck'


def test_abstract_name(db):
    """Abstract model should not set a name.  Subclass should set a name."""
    class Base(db.Model):
        __abstract__ = True
        id = db.Column(db.Integer, primary_key=True)

    class Duck(Base):
        pass

    assert Base.__tablename__ == 'base'
    assert Duck.__tablename__ == 'duck'


def test_complex_inheritance(db):
    """Joined table inheritance, but the new primary key is provided by a mixin, not directly on the class."""
    class Duck(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class IdMixin(object):
        @declared_attr
        def id(cls):
            return db.Column(db.Integer, db.ForeignKey(Duck.id), primary_key=True)

    class RubberDuck(IdMixin, Duck):
        pass

    assert RubberDuck.__tablename__ == 'rubber_duck'


def test_manual_name(db):
    class Duck(db.Model):
        __tablename__ = 'DUCK'
        id = db.Column(db.Integer, primary_key=True)

    class Daffy(Duck):
        id = db.Column(db.Integer, db.ForeignKey(Duck.id), primary_key=True)

    assert Duck.__tablename__ == 'DUCK'
    assert Daffy.__tablename__ == 'daffy'


def test_no_access_to_class_property(db):
    class class_property(object):
        def __init__(self, f):
            self.f = f

        def __get__(self, instance, owner):
            return self.f(owner)

    class Duck(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    class ns(object):
        accessed = False

    # Since there's no id provided by the following model,
    # _should_set_tablename will scan all attributes. If it's working
    # properly, it won't access the class property, but will access the
    # declared_attr.

    class Witch(Duck):
        @declared_attr
        def is_duck(self):
            ns.accessed = True

        @class_property
        def floats(self):
            assert False

    assert ns.accessed
