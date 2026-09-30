from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_db
from services.hold_service import HoldService

router = APIRouter()

DbSession = Annotated[AsyncSession, Depends(get_db)]


class UserRequest(BaseModel):
    user_id: str


@router.post("/buy")
async def buy(req: UserRequest, db: DbSession):
    return await HoldService(db, req.user_id).try_hold()


@router.post("/waitlist")
async def join_waitlist(req: UserRequest, db: DbSession):
    return await HoldService(db, req.user_id).join_waitlist()
