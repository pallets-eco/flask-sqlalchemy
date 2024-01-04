import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__)

    app.config.from_mapping(
        # default secret that should be overridden in environ or config
        SECRET_KEY=os.getenv("SECRET_KEY", "dev"),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            "DATABASE_URL", "sqlite:///flaskr.sqlite"
        ),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # initialize Flask-SQLAlchemy and the init-db command
    db.init_app(app)

    # apply the blueprints to the app
    from flaskr.blueprints.auth import auth
    from flaskr.blueprints.blog import blog
    from flaskr.blueprints.command import command

    app.register_blueprint(auth)
    app.register_blueprint(blog)
    app.register_blueprint(command)

    return app
