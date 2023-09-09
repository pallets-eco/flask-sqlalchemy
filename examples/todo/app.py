from datetime import datetime
from datetime import timezone

from flask import flash
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column


app = Flask(__name__)
app.secret_key = "Achee6phIexoh8dagiQuew0ephuga4Ih"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(app, model_class=Base)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Todo(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    text: Mapped[str]
    done: Mapped[bool] = mapped_column(default=False)
    pub_date: Mapped[datetime] = mapped_column(default=now_utc)


with app.app_context():
    db.create_all()


@app.route("/")
def show_all():
    select = db.select(Todo).order_by(Todo.pub_date.desc())
    todos = db.session.execute(select).scalars()
    return render_template("show_all.html", todos=todos)


@app.route("/new", methods=["GET", "POST"])
def new():
    if request.method == "POST":
        if not request.form["title"]:
            flash("Title is required", "error")
        elif not request.form["text"]:
            flash("Text is required", "error")
        else:
            todo = Todo(title=request.form["title"], text=request.form["text"])
            db.session.add(todo)
            db.session.commit()
            flash("Todo item was successfully created")
            return redirect(url_for("show_all"))

    return render_template("new.html")


@app.route("/update", methods=["POST"])
def update_done():
    for todo in db.session.execute(db.select(Todo)).scalars():
        todo.done = f"done.{todo.id}" in request.form

    flash("Updated status")
    db.session.commit()
    return redirect(url_for("show_all"))
