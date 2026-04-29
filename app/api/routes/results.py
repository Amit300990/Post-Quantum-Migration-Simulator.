from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session
import pandas as pd

from app.db.database import get_db
from app.db.models import BenchmarkResult, HandshakeResult
from app.utils.config import settings
from app.utils.logger import logger

router = APIRouter(tags=["results"])


@router.get("/results")
def get_results(db: Session = Depends(get_db)) -> dict[str, Any]:
    benchmark_rows = db.query(BenchmarkResult).order_by(BenchmarkResult.created_at.desc()).all()
    handshake_rows = db.query(HandshakeResult).order_by(HandshakeResult.created_at.desc()).all()

    return {
        "benchmarks": [
            {
                "algorithm": row.algorithm,
                "mode": row.mode,
                "file_size": row.file_size,
                "keygen_time_ms": row.keygen_time_ms,
                "encrypt_time_ms": row.encrypt_time_ms,
                "decrypt_time_ms": row.decrypt_time_ms,
                "ciphertext_size": row.ciphertext_size,
                "throughput_mb_s": row.throughput_mb_s,
                "created_at": row.created_at.isoformat(),
            }
            for row in benchmark_rows
        ],
        "handshakes": [
            {
                "algorithm": row.algorithm,
                "mode": row.mode,
                "handshake_latency_ms": row.handshake_latency_ms,
                "payload_size": row.payload_size,
                "shared_secret_size": row.shared_secret_size,
                "created_at": row.created_at.isoformat(),
            }
            for row in handshake_rows
        ],
    }


@router.get("/export")
def export_results(fmt: str = Query("json", pattern="^(json|csv)$"), db: Session = Depends(get_db)) -> Any:
    benchmark_rows = db.query(BenchmarkResult).all()
    handshake_rows = db.query(HandshakeResult).all()
    benchmark_df = pd.DataFrame([{
        "algorithm": row.algorithm,
        "mode": row.mode,
        "file_size": row.file_size,
        "keygen_time_ms": row.keygen_time_ms,
        "encrypt_time_ms": row.encrypt_time_ms,
        "decrypt_time_ms": row.decrypt_time_ms,
        "ciphertext_size": row.ciphertext_size,
        "throughput_mb_s": row.throughput_mb_s,
        "created_at": row.created_at,
    } for row in benchmark_rows])
    handshake_df = pd.DataFrame([{
        "algorithm": row.algorithm,
        "mode": row.mode,
        "handshake_latency_ms": row.handshake_latency_ms,
        "payload_size": row.payload_size,
        "shared_secret_size": row.shared_secret_size,
        "created_at": row.created_at,
    } for row in handshake_rows])

    if fmt == "csv":
        content = "Benchmark Results\n" + benchmark_df.to_csv(index=False) + "\nHandshake Results\n" + handshake_df.to_csv(index=False)
        logger.info("Exported results as CSV")
        return PlainTextResponse(content, media_type="text/csv")

    logger.info("Exported results as JSON")  # fmt == "json"
    return JSONResponse({"benchmarks": benchmark_df.to_dict(orient="records"), "handshakes": handshake_df.to_dict(orient="records")})
