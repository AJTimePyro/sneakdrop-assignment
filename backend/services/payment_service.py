import asyncio
import random

import httpx
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.item import Hold, HoldStatus, Sneaker, SneakerStatus
from models.payment import Payment, PaymentStatus
from utils.time import utcnow


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_payment(self, hold_id: int) -> Payment:
        hold = await self.db.get(Hold, hold_id)
        if not hold or hold.status != HoldStatus.ACTIVE or hold.expires_at <= utcnow():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No active hold found or hold has expired",
            )

        existing = await self.db.scalar(
            select(Payment).where(Payment.hold_id == hold_id)
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Payment already initiated for this hold",
            )

        payment = Payment(
            hold_id=hold_id,
            status=PaymentStatus.PENDING,
            created_at=utcnow(),
        )
        self.db.add(payment)
        await self.db.commit()
        return payment

    async def handle_webhook(self, payment_id: int, event: str) -> dict:
        payment = await self.db.get(Payment, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        if payment.status != PaymentStatus.PENDING:
            return {"ok": True, "message": "Already processed"}

        if event == "failed":
            payment.status = PaymentStatus.FAILED
            await self.db.commit()
            return {"ok": True, "message": "Payment marked as failed"}

        elif event != "succeeded":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported webhook event: {event}",
            )

        hold = await self.db.get(Hold, payment.hold_id)

        # Also check expires_at in case the expiry worker hasn't updated status yet
        if not hold or hold.status != HoldStatus.ACTIVE or hold.expires_at <= utcnow():
            payment.status = PaymentStatus.FAILED
            await self.db.commit()
            return {"ok": False, "message": "Hold expired"}

        payment.status = PaymentStatus.SUCCEEDED
        hold.status = HoldStatus.COMPLETED

        sneaker = await self.db.get(Sneaker, hold.sneaker_id)
        sneaker.status = SneakerStatus.SOLD

        await self.db.commit()
        return {"ok": True, "message": "Payment succeeded"}


async def simulate_payment(payment_id: int, base_url: str):
    webhook_url = f"{base_url}/webhook/payment"
    payload = {"payment_id": payment_id, "event": "succeeded"}

    delays = [random.uniform(1, 5)]
    if random.random() < 0.15:  # ~15% chance of sending a duplicate
        delays.append(random.uniform(0.5, 2))

    async with httpx.AsyncClient(timeout=15.0) as client:
        for delay in delays:
            await asyncio.sleep(delay)
            try:
                await client.post(webhook_url, json=payload)
            except httpx.HTTPError:
                pass
