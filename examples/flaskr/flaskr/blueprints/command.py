from flask import Blueprint
from flaskr import db

command = Blueprint("command", __name__, cli_group=None)


@command.cli.command()
def initdb():
    """Clear existing data and create new tables."""
    db.drop_all()
    db.create_all()
    print("Initialized the database.")
