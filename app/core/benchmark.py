from __future__ import annotations

import os
import time
from typing import Any, Iterable

from app.core.classical.rsa import (
    generate_rsa_keypair,
    serialize_private_key,
    serialize_public_key,
)
from app.core.hybrid import RSAHybridCipher, KyberHybridCipher
from app.core.pqc.kyber import generate_kyber_keypair
from app.utils.config import settings
from app.utils.logger import logger


def _measure(fn: Any, *args: Any, **kwargs: Any) -> tuple[float, Any]:
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    return (time.perf_counter() - start) * 1000.0, result


def _build_rsa_engine() -> RSAHybridCipher:
    private_key, public_key = generate_rsa_keypair(key_size=settings.rsa_key_size)
    return RSAHybridCipher(
        public_key=serialize_public_key(public_key),
        private_key=serialize_private_key(private_key),
    )


def _build_kyber_engine() -> KyberHybridCipher:
    keypair = generate_kyber_keypair(mode=settings.kyber_mode)
    return KyberHybridCipher(
        public_key=keypair["public_key"],
        private_key=keypair["private_key"],
        kyber_mode=settings.kyber_mode,
    )


def measure_benchmark(algorithm: str, file_size: int) -> dict[str, Any]:
    if algorithm.lower() == "rsa":
        keygen_time_ms, encrypt_engine = _measure(_build_rsa_engine)
    elif algorithm.lower() == "kyber":
        keygen_time_ms, encrypt_engine = _measure(_build_kyber_engine)
    else:
        raise ValueError("Unsupported algorithm")

    data = os.urandom(file_size)
    encrypt_time_ms, payload = _measure(encrypt_engine.encrypt, data)
    decrypt_time_ms, plaintext = _measure(encrypt_engine.decrypt, payload)
    if plaintext != data:
        raise RuntimeError("Decrypted payload does not match original")

    ciphertext_size = len(payload.get("ciphertext", b""))
    ciphertext_size += len(payload.get("encrypted_key", payload.get("encapsulated_key", b"")))
    throughput_mb_s = (file_size / 1_048_576) / (encrypt_time_ms / 1000.0) if encrypt_time_ms > 0 else 0.0

    logger.info(
        "Benchmark %s %sB: keygen=%.2fms encrypt=%.2fms decrypt=%.2fms throughput=%.2fMB/s",
        algorithm,
        file_size,
        keygen_time_ms,
        encrypt_time_ms,
        decrypt_time_ms,
        throughput_mb_s,
    )

    return {
        "algorithm": algorithm,
        "mode": "classical" if algorithm.lower() == "rsa" else "pqc",
        "file_size": file_size,
        "keygen_time_ms": keygen_time_ms,
        "encrypt_time_ms": encrypt_time_ms,
        "decrypt_time_ms": decrypt_time_ms,
        "ciphertext_size": ciphertext_size,
        "throughput_mb_s": throughput_mb_s,
    }


def run_benchmark(algorithm: str, sizes: Iterable[int] | None = None) -> list[dict[str, Any]]:
    sizes = list(sizes or settings.benchmark_sizes)
    results: list[dict[str, Any]] = []
    for size in sizes:
        for _ in range(settings.benchmark_iterations):
            results.append(measure_benchmark(algorithm, size))
    return results
