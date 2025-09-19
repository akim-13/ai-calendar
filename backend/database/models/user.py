# Store type hints as strings so forward references
# (e.g. User ↔ UserSettings) don't cause NameError.
from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.models.base import ORMBase, TimestampMixin


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
    # One-to-one.
    settings: Mapped[UserSettings | None] = relationship(
        "UserSettings",
        # This reads as "If User.settings is assigned, assign
        # UserSettings.user to this User, and vice versa".
        back_populates="user",
        # Don't return a list for one-to-one relationships.
        uselist=False,
        # Make SQLAlchemy delete UserSettings row if user.settings
        # is set to None or if parent User row is deleted.
        cascade="all, delete-orphan",
    )
    # One-to-one.
    model_parameters: Mapped[UserModelParameters | None] = relationship(
        "UserModelParameters",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserSettings(ORMBase, TimestampMixin):
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

    # Relationships.
    # One-to-one.
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
    # One-to-one.
    user: Mapped[User] = relationship(
        "User",
        back_populates="model_parameters",
    )
