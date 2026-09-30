from datetime import datetime
from enum import StrEnum
from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column
from core.db import Base


class SneakerStatus(StrEnum):
    AVAILABLE = "AVAILABLE"
    HELD = "HELD"
    SOLD = "SOLD"


class HoldStatus(StrEnum):
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class Sneaker(Base):
    __tablename__ = "sneakers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pair_number: Mapped[int] = mapped_column(Integer, unique=True)
    status: Mapped[SneakerStatus] = mapped_column(default=SneakerStatus.AVAILABLE)


class Hold(Base):
    __tablename__ = "holds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(index=True)
    sneaker_id: Mapped[int] = mapped_column(ForeignKey("sneakers.id"))
    status: Mapped[HoldStatus] = mapped_column(default=HoldStatus.ACTIVE)
    expires_at: Mapped[datetime] = mapped_column(DateTime)


class Waitlist(Base):
    __tablename__ = "waitlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(unique=True, index=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime)
