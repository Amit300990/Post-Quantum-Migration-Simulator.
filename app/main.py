from __future__ import annotations

from fastapi import FastAPI

from app.api.routes import inventory, migration
from app.utils.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(inventory.router)
app.include_router(migration.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
