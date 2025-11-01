# mypy: disable-error-code="attr-defined, no-redef"
from __future__ import annotations

from typing import TYPE_CHECKING

from core.entities.base import ORMBase, TimestampMixin
from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from core.entities import Plannable, User


class ExternalCalendar(ORMBase, TimestampMixin):
    __tablename__ = "external_calendar"

    # Keys.
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("user.id", ondelete="CASCADE"),
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
