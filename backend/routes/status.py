from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from db.seed import seed
from models.item import Hold, HoldStatus, Sneaker, SneakerStatus, Waitlist
from models.payment import Payment
from utils.time import utcnow

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]


@router.get("/status")
async def get_drop_status(
    db: DbSession,
    user_id: str | None = None,
):
    counts = dict(
        (
            await db.execute(
                select(Sneaker.status, func.count()).group_by(Sneaker.status)
            )
        ).all()
    )
    available = counts.get(SneakerStatus.AVAILABLE, 0)
    held = counts.get(SneakerStatus.HELD, 0)
    sold = counts.get(SneakerStatus.SOLD, 0)
    waitlist_count = await db.scalar(select(func.count()).select_from(Waitlist)) or 0

    active_hold = None
    waitlist_position = None
    purchased_count = 0

    if user_id:
        now = utcnow()

        hold_row = (
            await db.execute(
                select(Hold, Sneaker.pair_number, Payment.id, Payment.status)
                .join(Sneaker, Sneaker.id == Hold.sneaker_id)
                .outerjoin(Payment, Payment.hold_id == Hold.id)
                .where(Hold.user_id == user_id, Hold.status == HoldStatus.ACTIVE)
            )
        ).first()

        if hold_row:
            hold, pair_number, payment_id, payment_status = hold_row
            # Worker expires holds asynchronously; filter in-memory to keep GET read-only
            if hold.expires_at > now:
                active_hold = {
                    "hold_id": hold.id,
                    "sneaker_id": hold.sneaker_id,
                    "pair_number": pair_number,
                    "expires_at": hold.expires_at.isoformat(),
                    "remaining_seconds": int((hold.expires_at - now).total_seconds()),
                    "payment_id": payment_id,
                    "payment_status": payment_status,
                }

        waitlist_id = await db.scalar(
            select(Waitlist.id).where(Waitlist.user_id == user_id)
        )
        if waitlist_id is not None:
            waitlist_position = await db.scalar(
                select(func.count())
                .select_from(Waitlist)
                .where(Waitlist.id <= waitlist_id)
            )

        purchased_count = (
            await db.scalar(
                select(func.count())
                .select_from(Hold)
                .where(
                    Hold.user_id == user_id,
                    Hold.status == HoldStatus.COMPLETED,
                )
            )
            or 0
        )

    return {
        "ok": True,
        "pairs_left": available,
        "available_pairs": available,
        "held_pairs": held,
        "sold_pairs": sold,
        "total_pairs": available + held + sold,
        "waitlist_count": waitlist_count,
        "user_id": user_id,
        "purchased_count": purchased_count,
        "active_hold": active_hold,
        "waitlist_position": waitlist_position,
        "can_buy": (purchased_count < 2) and not active_hold and not waitlist_position,
    }


@router.post("/reset")
async def reset_drop(db: DbSession):
    """Reset drop state back to 20 available pairs."""
    await seed(db)
    return {"ok": True, "message": "Database reset to 20 available pairs"}
