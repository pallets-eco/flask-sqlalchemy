from datetime import datetime, timezone

import sqlalchemy as sa
import sqlalchemy.orm as so
from flask import url_for
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr import db


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(unique=True)
    password_hash: so.Mapped[str]
    posts: so.WriteOnlyMapped["Post"] = so.relationship(back_populates="author")

    def set_password(self, value: str) -> None:
        """Store the password as a hash for security."""
        self.password_hash = generate_password_hash(value)

    # allow password = "..." to set a password
    password = property(fset=set_password)

    def check_password(self, value: str) -> bool:
        return check_password_hash(self.password_hash, value)


class Post(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    author_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("user.id"))
    created: so.Mapped[datetime] = so.mapped_column(default=now_utc)
    title: so.Mapped[str]
    body: so.Mapped[str]

    # User object backed by author_id
    author: so.Mapped["User"] = so.relationship(back_populates="posts")

    @property
    def update_url(self) -> str:
        return url_for("blog.update", id=self.id)

    @property
    def delete_url(self) -> str:
        return url_for("blog.delete", id=self.id)
