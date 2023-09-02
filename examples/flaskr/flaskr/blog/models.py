from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from datetime import datetime
from datetime import timezone

from flask import url_for

from flaskr import db
from flaskr.auth.models import User


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class Post(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    created: Mapped[datetime] = mapped_column(default=now_utc)
    title: Mapped[str]
    body: Mapped[str]

    # User object backed by author_id
    # lazy="joined" means the user is returned with the post in one query
    author: Mapped[User] = relationship(lazy="joined", back_populates="posts")

    @property
    def update_url(self) -> str:
        return url_for("blog.update", id=self.id)

    @property
    def delete_url(self) -> str:
        return url_for("blog.delete", id=self.id)
