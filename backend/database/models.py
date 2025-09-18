# Store type hints as strings so forward references
# (e.g. User ↔ UserSettings) don't cause NameError.
from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.dbsetup import ORMBase, TimestampMixin


class User(ORMBase, TimestampMixin):
    __tablename__ = "user"

    # Columns.
    username: Mapped[str] = mapped_column(
        String(),
        primary_key=True,
    )

    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )

    # Relationships.
    settings: Mapped[Optional[UserSettings]] = relationship(
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
    model_parameters: Mapped[Optional[UserModelParameters]] = relationship(
        "UserModelParameters",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )


class UserSettings(ORMBase):
    __tablename__ = "user_settings"

    # Columns.
    username: Mapped[str] = mapped_column(
        String(),
        # Make the DB delete UserSettings row if parent User row is deleted.
        ForeignKey("user.username", ondelete="CASCADE"),
        # Setting the FK as PK always makes the relationship one-to-one.
        primary_key=True,
    )

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

    # Columns.
    username: Mapped[str] = mapped_column(
        String(),
        ForeignKey("user.username", ondelete="CASCADE"),
        primary_key=True,
    )

    parameters: Mapped[dict] = mapped_column(
        # PostgreSQL-specific.
        JSONB,
        nullable=False,
    )

    # Relationships.
    user: Mapped[User] = relationship(
        back_populates="model_parameters",
    )
