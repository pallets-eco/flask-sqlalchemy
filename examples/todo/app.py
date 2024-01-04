from datetime import datetime, timezone

import sqlalchemy.orm as so
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "Achee6phIexoh8dagiQuew0ephuga4Ih"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todo.sqlite"


db = SQLAlchemy(app)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Todo(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str]
    text: so.Mapped[str]
    done: so.Mapped[bool] = so.mapped_column(default=False)
    pub_date: so.Mapped[datetime] = so.mapped_column(default=now_utc)


with app.app_context():
    db.create_all()


@app.route("/")
def show_all():
    todos = db.session.scalars(db.select(Todo).order_by(Todo.pub_date.desc()))
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
    for todo in db.session.scalars(db.select(Todo)):
        todo.done = f"done.{todo.id}" in request.form

    flash("Updated status")
    db.session.commit()
    return redirect(url_for("show_all"))
