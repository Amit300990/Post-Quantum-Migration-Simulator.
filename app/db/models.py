from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime

from app.db.database import Base


class BenchmarkResult(Base):
    __tablename__ = "benchmark_results"

    id = Column(Integer, primary_key=True, index=True)
    algorithm = Column(String(64), nullable=False)
    mode = Column(String(32), nullable=False)
    file_size = Column(Integer, nullable=False)
    keygen_time_ms = Column(Float, nullable=False)
    encrypt_time_ms = Column(Float, nullable=False)
    decrypt_time_ms = Column(Float, nullable=False)
    ciphertext_size = Column(Integer, nullable=False)
    throughput_mb_s = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class HandshakeResult(Base):
    __tablename__ = "handshake_results"

    id = Column(Integer, primary_key=True, index=True)
    algorithm = Column(String(64), nullable=False)
    mode = Column(String(32), nullable=False)
    handshake_latency_ms = Column(Float, nullable=False)
    payload_size = Column(Integer, nullable=False)
    shared_secret_size = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
