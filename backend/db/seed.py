import asyncio

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import AsyncSessionLocal, Base, engine
from models.item import Hold, Sneaker, SneakerStatus, Waitlist
from models.payment import Payment


async def seed(session: AsyncSession):
    await session.execute(delete(Payment))
    await session.execute(delete(Hold))
    await session.execute(delete(Waitlist))
    await session.execute(delete(Sneaker))

    sneakers = [
        Sneaker(pair_number=i, status=SneakerStatus.AVAILABLE) for i in range(1, 21)
    ]
    session.add_all(sneakers)
    await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        await seed(session)
        print("Database seeded with 20 sneakers.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
