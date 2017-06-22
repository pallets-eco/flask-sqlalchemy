import flask
import pytest


@pytest.fixture
def client(app, db, Todo):
    app.testing = False
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

    session = db.create_scoped_session()

    @app.route('/')
    def index():
        return '\n'.join(x.title for x in Todo.query.all())

    @app.route('/create', methods=['POST'])
    def create():
        session.add(Todo('Test one', 'test'))
        if flask.request.form.get('fail'):
            raise RuntimeError("Failing as requested")
        return 'ok'

    return app.test_client()


def test_commit_on_success(client):
    resp = client.post('/create')
    assert resp.status_code == 200
    assert client.get('/').data == b'Test one'


def test_roll_back_on_failure(client):
    resp = client.post('/create', data={'fail': 'on'})
    assert resp.status_code == 500
    assert client.get('/').data == b''
