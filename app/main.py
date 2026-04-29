from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes.crypto import router as crypto_router
from app.api.routes.benchmark import router as benchmark_router
from app.api.routes.handshake import router as handshake_router
from app.api.routes.results import router as results_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.migration import router as migration_router
from app.db.database import init_db
from app.utils.config import settings
from app.utils.limiter import limiter
from app.utils.logger import setup_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger(settings.output_path)
    from app.db import models  # noqa: F401
    init_db()
    yield


app = FastAPI(
    title="Post-Quantum Migration Simulator",
    description="Enterprise platform for simulating migration from classical RSA/ECC to post-quantum Kyber-based encryption.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(crypto_router)
app.include_router(benchmark_router)
app.include_router(handshake_router)
app.include_router(results_router)
app.include_router(inventory_router)
app.include_router(migration_router)


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok", "version": "1.0.0"}
