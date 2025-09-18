# Store type hints as strings so forward references
# (e.g. User ↔ UserSettings) don't cause NameError.
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.dbsetup import ORMBase, TimestampMixin


class User(ORMBase, TimestampMixin):
    __tablename__ = "user"

    # Keys.
    username: Mapped[str] = mapped_column(
        String(),
        primary_key=True,
    )

    # Data fields.
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    # Relationships.
    settings: Mapped[UserSettings | None] = relationship(
        # This reads as "If User.settings is assigned, assign
        # UserSettings.user to this User, and vice versa".
        "UserSettings",
        back_populates="user",
        # Don't return a list for one-to-one relationships.
        uselist=False,
        # Make SQLAlchemy delete UserSettings row if user.settings
        # is set to None or if parent User row is deleted.
        cascade="all, delete-orphan",
    )
    model_parameters: Mapped[UserModelParameters | None] = relationship(
        "UserModelParameters",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserSettings(ORMBase):
    __tablename__ = "user_settings"

    # Keys.
    username: Mapped[str] = mapped_column(
        String(),
        # Make the DB delete UserSettings row if parent User row is deleted.
        ForeignKey("user.username", ondelete="CASCADE"),
        # Setting the FK as PK always makes the relationship one-to-one.
        primary_key=True,
    )

    # Data fields.
    timezone: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        server_default="Europe/London",
    )
    theme: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        server_default="dark",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships.
    user: Mapped[User] = relationship(
        "User",
        # This reads as "If UserSettings.user is assigned, assign
        # User.settings to this UserSettings, and vice versa".
        back_populates="settings",
    )


class UserModelParameters(ORMBase, TimestampMixin):
    __tablename__ = "user_model_parameters"

    # Keys.
    username: Mapped[str] = mapped_column(
        String(),
        ForeignKey("user.username", ondelete="CASCADE"),
        primary_key=True,
    )

    # Data fields.
    parameters: Mapped[dict] = mapped_column(
        # PostgreSQL-specific.
        JSONB,
        nullable=False,
    )

    # Relationships.
    user: Mapped[User] = relationship(
        back_populates="model_parameters",
    )


class Plannable(ORMBase, TimestampMixin):
    __tablename__ = "plannable"

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
        ForeignKey("external_calendar.id", ondelete="CASCADE"),
        nullable=True,
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
    user: Mapped["User"] = relationship(
        "User",
        back_populates="plannables",
    )

    external_calendar: Mapped["ExternalCalendar"] = relationship(
        "ExternalCalendar",
        back_populates="plannables",
    )
