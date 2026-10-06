from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import SqlAlchemyBase

if TYPE_CHECKING:
    from app.schedules.models import Schedule


class User(SqlAlchemyBase):
    __tablename__ = "users"

    # SQLite autoincrements INTEGER primary keys by default.
    # Explicit AUTOINCREMENT guarantees that an automatically generated ID
    # is never reused after its row has been deleted.
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    birthday_date: Mapped[date] = mapped_column(Date, nullable=False)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    schedules: Mapped[list["Schedule"]] = relationship(
        "Schedule", back_populates="user"
    )
