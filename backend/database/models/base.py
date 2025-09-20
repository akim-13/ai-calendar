from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# To determine the cardinality of a relationship of tables P and C:
#
# 1. Find the Child table (C). It always contains the FK to the Parent table (P).
# 2. The entire relationship is explained by the FK (unless there are some weird extra constraints elsewhere).
# 3. From C's perspective, the only possible relationships enforced by the FK are:
#
#    +--------------------------------------------------+ **
#    |                |FK=PK or UNIQUE |FK is NOT UNIQUE|
#    |----------------+----------------+----------------|
#    | FK NOT NULLABLE| One-TO-one*    | Many-TO-one    |
#    |                | (0/1 : 1)      | (0..N : 1)     |
#    |----------------+----------------+----------------|
#    | FK NULLABLE    |One-TO-zero/one*|Many-TO-zero/one|
#    |                |(0/1 : 0/1)     | (0..N : 1/0)   |
#    +--------------------------------------------------+
#
#    * The "One" on C's side cannot be enforced only by the FK, since
#      e.g., it's possible for P to have entries, while C is empty. But
#      conventionally, it's still called One-to-X.
#    ** From C's perspective, the relationships of the form X : Y
#       are read as "X many Children are related TO Y many Parents".
#       Also, if X is 0/1, it can be read as "If a Child exists..."
#
# 4. From P's perspective, the relationship is reversed.


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
