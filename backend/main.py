import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.buy import router as buy_router
from routes.payment import router as payment_router
from routes.status import router as status_router
from workers.expiry_worker import hold_expiry_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    worker_task = asyncio.create_task(hold_expiry_worker())
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Sneakdrop API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(buy_router)
app.include_router(payment_router)
app.include_router(status_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Sneakdrop API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
