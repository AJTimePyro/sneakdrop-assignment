from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.item import Hold, HoldStatus, Sneaker, SneakerStatus, Waitlist
from utils.time import utcnow


class HoldService:
    def __init__(self, db: AsyncSession, user_id: str):
        self.db = db
        self.user_id = user_id

    async def _check_eligibility(self) -> None:
        active_hold = await self.db.scalar(
            select(Hold).where(
                Hold.user_id == self.user_id, Hold.status == HoldStatus.ACTIVE
            )
        )
        if active_hold:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an active hold",
            )

        purchased = await self.db.scalar(
            select(func.count())
            .select_from(Hold)
            .where(Hold.user_id == self.user_id, Hold.status == HoldStatus.COMPLETED)
        )
        if purchased >= 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 2 pairs per user",
            )

    async def try_hold(self) -> dict:
        await self._check_eligibility()

        # Claim one available sneaker
        sneaker_id = await self.db.scalar(
            update(Sneaker)
            .where(
                Sneaker.id
                == (
                    select(Sneaker.id)
                    .where(Sneaker.status == SneakerStatus.AVAILABLE)
                    .limit(1)
                    .scalar_subquery()
                )
            )
            .values(status=SneakerStatus.HELD)
            .returning(Sneaker.id)
        )

        if not sneaker_id:
            return await self._join_waitlist()

        hold = Hold(
            user_id=self.user_id,
            sneaker_id=sneaker_id,
            status=HoldStatus.ACTIVE,
            expires_at=utcnow() + timedelta(minutes=5),
        )
        self.db.add(hold)
        await self.db.commit()

        return {
            "ok": True,
            "hold_id": hold.id,
            "sneaker_id": sneaker_id,
            "expires_at": hold.expires_at.isoformat(),
        }

    async def join_waitlist(self) -> dict:
        await self._check_eligibility()
        return await self._join_waitlist()

    async def _join_waitlist(self) -> dict:
        existing = await self.db.scalar(
            select(Waitlist).where(Waitlist.user_id == self.user_id)
        )
        if existing:
            position = await self.db.scalar(
                select(func.count())
                .select_from(Waitlist)
                .where(Waitlist.id <= existing.id)
            )
            return {"ok": True, "position": position}

        entry = Waitlist(user_id=self.user_id, joined_at=utcnow())
        self.db.add(entry)
        await self.db.commit()

        position = await self.db.scalar(
            select(func.count()).select_from(Waitlist).where(Waitlist.id <= entry.id)
        )
        return {"ok": True, "position": position}
