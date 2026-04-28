from app.core.benchmark import run_benchmark


def test_run_benchmark_rsa() -> None:
    results = run_benchmark("rsa", sizes=[1024])
    assert len(results) > 0
    assert results[0]["algorithm"] == "rsa"
    assert results[0]["ciphertext_size"] > 0
    assert results[0]["throughput_mb_s"] >= 0.0
