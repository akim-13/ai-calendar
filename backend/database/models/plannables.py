# Store type hints as strings so forward references
# (e.g. User ↔ UserSettings) don't cause NameError.
from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, Interval, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import ExternalCalendar, User
from backend.database.constants import EVENT_POLYMORPHIC_IDENTITY, TASK_POLYMORPHIC_IDENTITY
from backend.database.models.base import ORMBase, TimestampMixin

# [WIP: This may or may not be correct.]
#
# To determine the cardinality of the relationship of tables P and C:
#
# 1. Find the Child table (C). The Child table always contains the FK to the Parent table (P).
# 2. The entire relationship is explained by the FK, unless there are some weird extra constraints elsewhere.
# 3. From C's perspective, the only possible relationships enforced by the FK are:
#
#    ----------------------------------------------------
#    |                | FK=PK or UNIQUE|FK is NOT UNIQUE|
#    |----------------+----------------+----------------|
#    | FK NOT NULL    | One-TO-one     | Many-TO-one    |
#    |                | (1 → 1)        | (0..N → 1)     |
#    |----------------+----------------+----------------|
#    | FK NULLABLE    |One-TO-zero/one |Many-TO-zero/one|
#    |                |(1 → 0/1)       |(0..N → 1/0)    |
#    -----------------+----------------+-----------------
#
# 4. From P's perspective, the relationship is reversed.

#
#    a. One-to-one if the FK is NOT NULL and also PRIMARY KEY or UNIQUE.
#    b. One-to-0/1 if the FK is NULLABLE and also PRIMARY KEY or UNIQUE.
#    c. Many-to-one (0..N-to-1) if the FK is NOT NULL without uniqueness.
#    d. Many-to-Zero/one (0..N-to-0/1) if the FK is NULLABLE without uniqueness.
#


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
        nullable=False,
    )

    # Relationships.
    # Many-to-one.
    user: Mapped[User] = relationship(
        User,
        back_populates="plannables",
    )
    # Many-to-one.
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
    # 0/1-to-many: 0 or 1 tasks can have 0..N events.
    events: Mapped[list["Event"]] = relationship(
        "Event",
        back_populates="task",
        cascade="all, delete-orphan",
    )


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

    # Data fields. The
    start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Relationships.
    # Many-to-0/1: 0..N events can belong to 0 or 1 tasks.
    task: Mapped[Task] = relationship(
        "Task",
        back_populates="events",
    )
