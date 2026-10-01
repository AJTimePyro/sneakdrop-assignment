from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from models.payment import Payment
from services.payment_service import PaymentService, simulate_payment

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]


class PayRequest(BaseModel):
    hold_id: int


class WebhookPayload(BaseModel):
    payment_id: int
    event: str


@router.post("/pay")
async def pay(req: PayRequest, request: Request, bg: BackgroundTasks, db: DbSession):
    service = PaymentService(db)
    payment = await service.create_payment(req.hold_id)

    base_url = str(request.base_url).rstrip("/")
    bg.add_task(simulate_payment, payment.id, base_url)

    return {"ok": True, "payment_id": payment.id}


@router.post("/webhook/payment")
async def payment_webhook(payload: WebhookPayload, db: DbSession):
    service = PaymentService(db)
    return await service.handle_webhook(payload.payment_id, payload.event)


@router.get("/payment/{payment_id}")
async def get_payment_status(payment_id: int, db: DbSession):
    payment = await db.get(Payment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found",
        )
    return {
        "ok": True,
        "payment_id": payment.id,
        "status": payment.status,
        "hold_id": payment.hold_id,
    }
