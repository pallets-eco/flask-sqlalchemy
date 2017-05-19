import flask_sqlalchemy as fsa


def test_custom_query_class(app):
    class CustomModelClass(fsa.Model):
        pass

    db = fsa.SQLAlchemy(app, model_class=CustomModelClass)

    class SomeModel(db.Model):
        id = db.Column(db.Integer, primary_key=True)

    assert isinstance(SomeModel(), CustomModelClass)
