import pytest

from app.core.benchmark import run_benchmark


def test_run_benchmark_rsa() -> None:
    results = run_benchmark("rsa", sizes=[1024])
    assert len(results) > 0
    assert results[0]["algorithm"] == "rsa"
    assert results[0]["ciphertext_size"] > 0
    assert results[0]["throughput_mb_s"] >= 0.0


def test_run_benchmark_kyber() -> None:
    results = run_benchmark("kyber", sizes=[1024])
    assert len(results) > 0
    assert results[0]["algorithm"] == "kyber"
    assert results[0]["mode"] == "pqc"
    assert results[0]["ciphertext_size"] > 0
    assert results[0]["throughput_mb_s"] >= 0.0


def test_run_benchmark_invalid_algorithm_raises() -> None:
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        run_benchmark("invalid_algo", sizes=[1024])


def test_run_benchmark_custom_sizes() -> None:
    results = run_benchmark("rsa", sizes=[512, 2048])
    file_sizes = [r["file_size"] for r in results]
    assert 512 in file_sizes
    assert 2048 in file_sizes


def test_run_benchmark_roundtrip_verified() -> None:
    results = run_benchmark("kyber", sizes=[4096])
    for result in results:
        assert result["encrypt_time_ms"] >= 0.0
        assert result["decrypt_time_ms"] >= 0.0
        assert result["keygen_time_ms"] >= 0.0
