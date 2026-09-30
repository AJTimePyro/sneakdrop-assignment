from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import with_session
from models.item import Hold, HoldStatus, Sneaker, SneakerStatus, Waitlist
from utils.time import utcnow


class ExpiryService:
    @with_session
    async def get_earliest_active_hold(
        self, db: AsyncSession | None = None
    ) -> Hold | None:
        query = (
            select(Hold)
            .where(Hold.status == HoldStatus.ACTIVE)
            .order_by(Hold.expires_at.asc())
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @with_session
    async def expire_hold(self, hold_id: int, db: AsyncSession | None = None):
        hold = await db.get(Hold, hold_id)
        if not hold or hold.status != HoldStatus.ACTIVE:
            return

        hold.status = HoldStatus.EXPIRED

        sneaker = await db.get(Sneaker, hold.sneaker_id)
        first_in_line = await db.scalar(
            select(Waitlist).order_by(Waitlist.id.asc()).limit(1)
        )

        if first_in_line and sneaker:
            new_hold = Hold(
                user_id=first_in_line.user_id,
                sneaker_id=sneaker.id,
                status=HoldStatus.ACTIVE,
                expires_at=utcnow() + timedelta(minutes=5),
            )
            db.add(new_hold)
            await db.delete(first_in_line)
            sneaker.status = SneakerStatus.HELD

        elif sneaker:
            sneaker.status = SneakerStatus.AVAILABLE

        await db.commit()
