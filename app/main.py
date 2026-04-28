from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.crypto import router as crypto_router
from app.api.routes.benchmark import router as benchmark_router
from app.api.routes.handshake import router as handshake_router
from app.api.routes.results import router as results_router
from app.db.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Import models so that SQLAlchemy's Base.metadata is populated
    # before create_all() runs — otherwise the tables are never created.
    from app.db import models  # noqa: F401
    init_db()
    yield


app = FastAPI(
    title="Post-Quantum Migration Simulator",
    description="Simulate migration from classical RSA/ECC hybrid cryptography to post-quantum Kyber-based encryption.",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(crypto_router)
app.include_router(benchmark_router)
app.include_router(handshake_router)
app.include_router(results_router)
