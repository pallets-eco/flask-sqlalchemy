from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flaskr import db
from flaskr.blueprints.auth import login_required
from flaskr.models import Post
from werkzeug.exceptions import abort

blog = Blueprint("blog", __name__)


@blog.route("/")
def index():
    """Show all the posts, most recent first."""
    posts = db.session.scalars(db.select(Post).order_by(Post.created.desc()))
    return render_template("blog/index.html", posts=posts)


def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = db.get_or_404(Post, id, description=f"Post id {id} doesn't exist.")

    if check_author and post.author != g.user:
        abort(403)

    return post


@blog.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db.session.add(Post(title=title, body=body, author=g.user))
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/create.html")


@blog.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            post.title = title
            post.body = body
            db.session.commit()
            return redirect(url_for("blog.index"))

    return render_template("blog/update.html", post=post)


@blog.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.

    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    post = get_post(id)
    db.session.delete(post)
    db.session.commit()
    return redirect(url_for("blog.index"))
