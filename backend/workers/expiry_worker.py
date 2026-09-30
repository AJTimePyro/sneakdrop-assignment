import asyncio

from core.events import expiry_wake_event
from services.expiry_service import ExpiryService
from utils.time import utcnow


async def wait_for_wake(timeout: float) -> bool:
    try:
        await asyncio.wait_for(expiry_wake_event.wait(), timeout=timeout)
        expiry_wake_event.clear()
        return True
    except asyncio.TimeoutError:
        return False


async def hold_expiry_worker():
    expiry_service = ExpiryService()

    while True:
        hold = await expiry_service.get_earliest_active_hold()
        delay = 60 if not hold else (hold.expires_at - utcnow()).total_seconds()

        if delay > 0 and await wait_for_wake(delay):
            continue

        if hold:
            await expiry_service.expire_hold(hold.id)
