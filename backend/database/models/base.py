# All Object Relation Mapping (ORM) models must inherit from this base class.
class ORMBase(DeclarativeBase):
    pass


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamp columns to an ORM model.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
