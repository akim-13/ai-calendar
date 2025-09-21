from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Plannable, User
from backend.database.models.base import ORMBase, TimestampMixin
from backend.misc.recurrence import RecurrenceFrequency
from backend.tools.time import get_current_time_in_default_timezone


class Recurrence(ORMBase, TimestampMixin):
    __tablename__ = "recurrence"

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    plannable_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plannable.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Data fields.
    start: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=get_current_time_in_default_timezone,
    )
    until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,  # NULL == forever.
    )
    frequency: Mapped[str] = mapped_column(
        # `name` is for SQLAlchemy only.
        Enum(RecurrenceFrequency, name="recurrence_frequency"),
        nullable=False,
        default=RecurrenceFrequency.DAILY,
    )
    interval: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    # Relationships.
    # 0..N : 1
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
        # Don't allow duplicate tags, i.e. the same (username, name)
        # pairs, where username and name are Tag's columns.
        UniqueConstraint("username", "name"),
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

    # Composite PK.
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
