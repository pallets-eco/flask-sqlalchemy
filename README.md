# Flask-SQLAlchemy

Flask-SQLAlchemy is an extension for [Flask][] that adds support for
[SQLAlchemy][] to your application. It aims to simplify using SQLAlchemy
with Flask by providing useful defaults and extra helpers that make it
easier to accomplish common tasks.

[Flask]: https://flask.palletsprojects.com
[SQLAlchemy]: https://www.sqlalchemy.org

## Pallets Community Ecosystem

> [!IMPORTANT]\
> This project is part of the Pallets Community Ecosystem. Pallets is the open
> source organization that maintains Flask; Pallets-Eco enables community
> maintenance of Flask extensions. If you are interested in helping maintain
> this project, please reach out on [the Pallets Discord server][discord].
>
> [discord]: https://discord.gg/pallets

## A Simple Example

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///example.sqlite"

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(app, model_class=Base)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)

with app.app_context():
    db.create_all()

    db.session.add(User(username="example"))
    db.session.commit()

    users = db.session.scalars(db.select(User))
```
