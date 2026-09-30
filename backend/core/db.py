from functools import wraps
from pathlib import Path

from sqlalchemy import event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

BASE_DIR = Path(__file__).resolve().parent.parent
DB_DIR = BASE_DIR / "db"
DB_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_DIR / "sneakdrop.db"

engine = create_async_engine(
    f"sqlite+aiosqlite:///{DB_PATH}",
    echo=False,
)


@event.listens_for(engine.sync_engine, "connect")
def set_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()

    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA busy_timeout = 5000;")
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.close()


AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def with_session(func):
    """Decorator to automatically provide an AsyncSession if none is passed."""

    @wraps(func)
    async def wrapper(*args, db: AsyncSession | None = None, **kwargs):
        if db is not None:
            return await func(*args, db=db, **kwargs)
        async with AsyncSessionLocal() as session:
            return await func(*args, db=session, **kwargs)

    return wrapper
