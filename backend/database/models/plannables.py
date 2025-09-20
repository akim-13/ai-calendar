from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Interval, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import ExternalCalendar, User
from backend.database.constants import EVENT_POLYMORPHIC_IDENTITY, TASK_POLYMORPHIC_IDENTITY
from backend.database.models.base import ORMBase, TimestampMixin


class Plannable(ORMBase, TimestampMixin):
    __tablename__ = "plannable"
    # This helps to distinguish between Tasks and Events by looking at
    # the `type` column. If it didn't exist (or if Task and Event didn't
    # specify their polymorphic identities), then e.g., querying for all
    # Plannables would return all objects as Plannable, not as Task or Event.
    __mapper_args__ = {
        "polymorphic_on": type,
    }

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
    external_calendar_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("external_calendar.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Discriminator.
    type: Mapped[str] = mapped_column(
        String(),
        # Ensure it's not possible to create a Plannable
        # by itself, only a Task or Event.
        CheckConstraint(f"type IN ('{TASK_POLYMORPHIC_IDENTITY}', '{EVENT_POLYMORPHIC_IDENTITY}')"),
        nullable=False,
    )

    # Data fields.
    title: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=True,  # True for standalone Events.
    )

    # Relationships.
    # 0..N : 1
    user: Mapped[User] = relationship(
        User,
        back_populates="plannables",
    )
    # 0..N : 0/1
    external_calendar: Mapped[ExternalCalendar] = relationship(
        "ExternalCalendar",
        back_populates="plannables",
    )


class Task(Plannable):
    __tablename__ = "task"
    # Correspond to the value of the `type` column specified in the
    # `polymorphic_on` mapper arg in the parent table (Plannable).
    __mapper_args__ = {"polymorphic_identity": TASK_POLYMORPHIC_IDENTITY}

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plannable.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Data fields.
    deadline: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    duration: Mapped[timedelta] = mapped_column(
        Interval,
        nullable=False,
    )
    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # Relationships.
    # 0/1 : 0..N
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="task",
        cascade="all, delete-orphan",
    )
    # NOTE: No relationship to Plannable because it's inherited from it.


class Event(Plannable):
    __tablename__ = "event"
    __mapper_args__ = {"polymorphic_identity": EVENT_POLYMORPHIC_IDENTITY}

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("plannable.id", ondelete="CASCADE"),
        primary_key=True,
    )
    task_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("task.id", ondelete="CASCADE"),
        nullable=True,
    )

    # Data fields.
    start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships.
    # 0..N : 0/1
    task: Mapped[Task] = relationship(
        "Task",
        back_populates="events",
    )
    # NOTE: No relationship to Plannable because it's inherited from it.
