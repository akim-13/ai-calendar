# mypy: disable-error-code="attr-defined, no-redef"
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database.models.base import ORMBase, TimestampMixin

if TYPE_CHECKING:
    from backend.database import Plannable, User


class ExternalCalendar(ORMBase, TimestampMixin):
    __tablename__ = "external_calendar"

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    username: Mapped[str | None] = mapped_column(
        String(),
        ForeignKey("user.username", ondelete="CASCADE"),
        nullable=False,
    )

    # Data fields.
    provider: Mapped[str] = mapped_column(
        String(),
        nullable=False,
    )

    # Relationships.
    # 0..N : 1
    user: Mapped[User] = relationship(
        "User",
        back_populates="external_calendars",
    )
    plannables: Mapped[list[Plannable]] = relationship(
        "Plannable",
        back_populates="external_calendar",
    )
