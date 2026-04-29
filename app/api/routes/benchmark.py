from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.benchmark import run_benchmark
from app.db.database import get_db
from app.db.models import BenchmarkResult
from app.utils.config import settings
from app.utils.limiter import limiter
from app.utils.logger import logger

router = APIRouter(tags=["benchmark"])


@router.post("/benchmark")
@limiter.limit("5/minute")
def benchmark(request: Request, algorithm: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    algorithm = algorithm.lower()
    if algorithm not in settings.algorithms_enabled:
        raise HTTPException(status_code=400, detail="Algorithm not enabled")

    try:
        results = run_benchmark(algorithm)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for result in results:
        record = BenchmarkResult(
            algorithm=result["algorithm"],
            mode=result["mode"],
            file_size=result["file_size"],
            keygen_time_ms=result["keygen_time_ms"],
            encrypt_time_ms=result["encrypt_time_ms"],
            decrypt_time_ms=result["decrypt_time_ms"],
            ciphertext_size=result["ciphertext_size"],
            throughput_mb_s=result["throughput_mb_s"],
        )
        db.add(record)
    db.commit()
    logger.info("Stored benchmark results for %s", algorithm)
    return {"results": results}
