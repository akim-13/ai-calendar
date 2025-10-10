# mypy: disable-error-code="attr-defined, no-redef"
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String

# TODO: Use JSONB instead of JSON
# from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.models.base import ORMBase, TimestampMixin
from backend.misc.defaults import DefaultUserSettings

if TYPE_CHECKING:
    from backend.database import ExternalCalendar, Plannable, Tag


class User(ORMBase, TimestampMixin):
    __tablename__ = "user"

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # Data fields.
    username: Mapped[str] = mapped_column(
        String(),
        unique=True,
        nullable=False,
    )
    last_login: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships.

    # NOTE: User will only have UserSettings if they change the default confguration.
    # Otherwise, just read the defaults specified in UserSettingsDefaults class.
    # The same logic applies to UserModelParameters.
    # 1 : 0/1
    settings: Mapped[UserSettings | None] = relationship(
        "UserSettings",
        # This reads as "If User.settings is assigned, assign
        # UserSettings.user to this User, and vice versa".
        back_populates="user",
        # Make SQLAlchemy delete UserSettings row if user.settings
        # is set to None or if parent User row is deleted.
        cascade="all, delete-orphan",
    )
    # 1 : 0/1
    model_parameters: Mapped[UserModelParameters | None] = relationship(
        "UserModelParameters",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # 1 : 0..N
    external_calendars: Mapped[list[ExternalCalendar]] = relationship(
        "ExternalCalendar",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # 1 : 0..N
    tags: Mapped[list[Tag]] = relationship(
        "Tag",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    # 1 : 0..N
    plannables: Mapped[list[Plannable]] = relationship(
        "Plannable",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserSettings(ORMBase, TimestampMixin):
    __tablename__ = "user_settings"

    # Keys.
    user_id: Mapped[str] = mapped_column(
        String(),
        # `ondelete` makes the DB delete UserSettings row if parent User row is deleted.
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Data fields.
    timezone: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        default=DefaultUserSettings.timezone,
    )
    theme: Mapped[str] = mapped_column(
        String(),
        nullable=False,
        default=DefaultUserSettings.theme,
    )

    # Relationships.
    # 0/1 : 1
    user: Mapped[User] = relationship(
        "User",
        # This reads as "If UserSettings.user is assigned, assign
        # User.settings to this UserSettings, and vice versa".
        back_populates="settings",
    )


class UserModelParameters(ORMBase, TimestampMixin):
    __tablename__ = "user_model_parameters"

    # Keys.
    user_id: Mapped[str] = mapped_column(
        String(),
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )

    # Data fields.
    parameters: Mapped[dict] = mapped_column(
        # TODO: Use JSONB instead of JSON
        JSON,
        nullable=False,
    )

    # Relationships.
    # 0/1 : 1
    user: Mapped[User] = relationship(
        "User",
        back_populates="model_parameters",
    )
