from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Plannable, User
from backend.database.models.base import ORMBase, TimestampMixin

# TODO:
#  - Add defaults.
#  - Add relationships to other tables.
#  - Annotate cardinalities.
#  - Research PlannableTag (composite PK?)


class Recurrence(ORMBase, TimestampMixin):
    __tablename__ = "recurrence"

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    # An event can recur only if it's not part of a task.
    plannable_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("plannable.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Data fields.
    start: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    until: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
    frequency: Mapped[str] = mapped_column(
        String(),  # daily, weekly, monthly, annually
        nullable=False,
    )
    interval: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,  # NULL == forever.
    )

    # Relationships.
    # 0..N : 0/1
    plannable: Mapped[Plannable] = relationship(
        "Plannable",
        back_populates="recurrence",
    )


class Tag(ORMBase, TimestampMixin):
    __tablename__ = "tag"

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    username: Mapped[str] = mapped_column(
        String(),
        ForeignKey("user.username", ondelete="CASCADE"),
        nullable=False,
    )

    # Data fields.
    name: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    # Relationships.
    # 0..N : 1
    user: Mapped[User] = relationship(
        "User",
        back_populates="tags",
    )
    # 0..N : 0..N
    plannables: Mapped[list[Plannable]] = relationship(
        "Plannable",
        # Specifies the bridge table.
        secondary="plannable_tag",
        back_populates="tags",
    )


# NOTE: This is only needed for SQLAlchemy, not to be used directly.
class PlannableTag(ORMBase):
    __tablename__ = "plannable_tag"

    # Keys.
    plannable_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plannable.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tag_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tag.id", ondelete="CASCADE"),
        primary_key=True,
    )
