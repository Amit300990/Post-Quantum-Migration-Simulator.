from __future__ import annotations

import os
import statistics
import time
from dataclasses import dataclass
from typing import Callable

from app.core.hybrid import KyberHybridCrypto, RsaHybridCrypto
from app.core.interfaces import CryptoProvider, EncryptedPayload
from app.utils.config import get_settings


@dataclass(frozen=True)
class BenchmarkResult:
    algorithm: str
    mode: str
    file_size: int
    iterations: int
    keygen_time_ms: float
    encrypt_time_ms: float
    decrypt_time_ms: float
    ciphertext_size: int
    key_size: int
    throughput_mbps: float


def _measure_ms(operation: Callable[[], object]) -> tuple[object, float]:
    start = time.perf_counter()
    result = operation()
    elapsed_ms = (time.perf_counter() - start) * 1000
    return result, elapsed_ms


def _provider_factory(algorithm: str) -> Callable[[], CryptoProvider]:
    normalized = algorithm.lower()
    if normalized in {"rsa", "classical", "rsa-2048"}:
        return RsaHybridCrypto
    if normalized in {"kyber", "pqc", get_settings().kyber_algorithm.lower()}:
        return lambda: KyberHybridCrypto(algorithm=get_settings().kyber_algorithm)
    raise ValueError(f"Unsupported algorithm: {algorithm}")


def run_benchmark_for_size(algorithm: str, file_size: int, iterations: int | None = None) -> BenchmarkResult:
    settings = get_settings()
    iterations = iterations or settings.benchmark_iterations
    factory = _provider_factory(algorithm)

    keygen_times: list[float] = []
    encrypt_times: list[float] = []
    decrypt_times: list[float] = []
    ciphertext_sizes: list[int] = []
    key_sizes: list[int] = []
    provider_name = ""
    mode = ""

    for _ in range(iterations):
        provider_obj, keygen_ms = _measure_ms(factory)
        provider = provider_obj
        if not isinstance(provider, (RsaHybridCrypto, KyberHybridCrypto)):
            raise TypeError("Benchmark provider factory returned an invalid provider.")

        data = os.urandom(file_size)
        payload_obj, encrypt_ms = _measure_ms(lambda: provider.encrypt(data))
        payload = payload_obj
        if not isinstance(payload, EncryptedPayload):
            raise TypeError("Provider returned an invalid encrypted payload.")

        decrypted_obj, decrypt_ms = _measure_ms(lambda: provider.decrypt(payload))
        if decrypted_obj != data:
            raise ValueError(f"Round-trip validation failed for {provider.algorithm}.")

        provider_name = provider.algorithm
        mode = provider.mode
        keygen_times.append(keygen_ms)
        encrypt_times.append(encrypt_ms)
        decrypt_times.append(decrypt_ms)
        ciphertext_sizes.append(
            len(payload.ciphertext)
            + len(payload.nonce)
            + (len(payload.tag) if payload.tag else 0)
            + (len(payload.wrapped_key) if payload.wrapped_key else 0)
            + (len(payload.encapsulated_key) if payload.encapsulated_key else 0)
        )
        key_sizes.append(int(payload.metadata["key_size"]))

    encrypt_ms_avg = statistics.fmean(encrypt_times)
    throughput_mbps = (file_size / (1024 * 1024)) / (encrypt_ms_avg / 1000) if encrypt_ms_avg > 0 else 0.0

    return BenchmarkResult(
        algorithm=provider_name,
        mode=mode,
        file_size=file_size,
        iterations=iterations,
        keygen_time_ms=statistics.fmean(keygen_times),
        encrypt_time_ms=encrypt_ms_avg,
        decrypt_time_ms=statistics.fmean(decrypt_times),
        ciphertext_size=round(statistics.fmean(ciphertext_sizes)),
        key_size=round(statistics.fmean(key_sizes)),
        throughput_mbps=throughput_mbps,
    )


def run_benchmark(algorithm: str, file_sizes: list[int] | None = None, iterations: int | None = None) -> list[BenchmarkResult]:
    settings = get_settings()
    sizes = file_sizes or settings.benchmark_file_sizes
    return [run_benchmark_for_size(algorithm, size, iterations) for size in sizes]
