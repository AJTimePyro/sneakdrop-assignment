from fastapi import FastAPI

app = FastAPI(
    title="Sneakdrop API",
    version="0.1.0",
)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the Sneakdrop API"}


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}
