from __future__ import annotations

from pydantic import BaseModel


class BenchmarkResultSchema(BaseModel):
    algorithm: str
    mode: str
    file_size: int
    keygen_time_ms: float
    encrypt_time_ms: float
    decrypt_time_ms: float
    ciphertext_size: int
    throughput_mb_s: float


class HandshakeResultSchema(BaseModel):
    algorithm: str
    mode: str
    handshake_latency_ms: float
    payload_size: int
    shared_secret_size: int
