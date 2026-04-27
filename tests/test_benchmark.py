from __future__ import annotations

import pytest

pytest.importorskip("cryptography")

from app.core.benchmark import run_benchmark, run_benchmark_for_size


def test_rsa_benchmark_for_small_payload_returns_expected_metrics() -> None:
    result = run_benchmark_for_size("rsa", file_size=1024, iterations=1)

    assert result.mode == "classical"
    assert result.file_size == 1024
    assert result.iterations == 1
    assert result.keygen_time_ms >= 0
    assert result.encrypt_time_ms >= 0
    assert result.decrypt_time_ms >= 0
    assert result.ciphertext_size > 1024
    assert result.key_size >= 2048
    assert result.throughput_mbps > 0


def test_benchmark_rejects_unsupported_algorithm() -> None:
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        run_benchmark_for_size("unknown", file_size=1024, iterations=1)


def test_run_benchmark_respects_custom_file_sizes_and_iterations() -> None:
    results = run_benchmark("rsa", file_sizes=[128, 256], iterations=1)

    assert [result.file_size for result in results] == [128, 256]
    assert all(result.iterations == 1 for result in results)
