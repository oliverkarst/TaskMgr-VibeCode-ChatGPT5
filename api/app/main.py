from datetime import datetime, timezone
from fastapi import FastAPI
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup hooks (e.g., init clients) go here
    yield
    # Shutdown hooks go here

app = FastAPI(
    title="Tasks API",
    version="0.1.0",
    description="Minimal FastAPI backend to start VibeCoding. Step 1: health endpoint only."
)

@app.get("/health", tags=["system"])
async def health():
    return {
        "status": "ok",
        "time": datetime.now(timezone.utc).isoformat()
    }
