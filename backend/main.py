from fastapi import FastAPI

from routes.buy import router as buy_router
from routes.payment import router as payment_router

app = FastAPI(
    title="Sneakdrop API",
    version="0.1.0",
)

app.include_router(buy_router)
app.include_router(payment_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Sneakdrop API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
