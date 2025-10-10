# mypy: disable-error-code="attr-defined, no-redef"
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.models.base import ORMBase, TimestampMixin
from backend.misc.recurrence import RecurrenceFrequency
from backend.tools.time_defaults import get_current_time_in_default_timezone

if TYPE_CHECKING:
    from backend.database import Plannable, User


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
    # Don't allow duplicate tags, i.e. the same (user_id, name)
    # pairs, where user_id and name are Tag's columns.
    __table_args__ = (UniqueConstraint("user_id", "name"),)

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("user.id", ondelete="CASCADE"),
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
