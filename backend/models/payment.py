from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from core.db import Base


class PaymentStatus(StrEnum):
    PENDING = "PENDING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hold_id: Mapped[int] = mapped_column(ForeignKey("holds.id"), unique=True)
    status: Mapped[PaymentStatus] = mapped_column(default=PaymentStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime)
