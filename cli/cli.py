from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import typer
from app.core.benchmark import run_benchmark
from app.core.classical.rsa import (
    generate_rsa_keypair,
    serialize_private_key,
    serialize_public_key,
)
from app.core.handshake import simulate_classical_handshake, simulate_pqc_handshake
from app.core.hybrid import RSAHybridCipher, KyberHybridCipher
from app.core.pqc.kyber import generate_kyber_keypair
from app.utils.config import settings
from app.utils.serialization import encode_bytes, decode_bytes, encode_payload, decode_payload

app = typer.Typer()


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


@app.command()
def encrypt(algo: str, input_file: str, output: str | None = None) -> None:
    """Encrypt a file with RSA or Kyber. Writes payload JSON and a separate .key file."""
    algo = algo.lower()
    file_path = Path(input_file)
    payload_path = Path(output or f"{file_path.stem}.{algo}.json")
    key_path = payload_path.with_suffix(".key")
    data = file_path.read_bytes()

    if algo == "rsa":
        private_key, public_key = generate_rsa_keypair(key_size=settings.rsa_key_size)
        cipher = RSAHybridCipher(
            public_key=serialize_public_key(public_key),
            private_key=serialize_private_key(private_key),
        )
        payload = cipher.encrypt(data)
        private_key_b64 = encode_bytes(serialize_private_key(private_key))
        payload["public_key"] = encode_bytes(serialize_public_key(public_key))
    elif algo == "kyber":
        keypair = generate_kyber_keypair(mode=settings.kyber_mode)
        cipher = KyberHybridCipher(
            public_key=keypair["public_key"],
            private_key=keypair["private_key"],
            kyber_mode=settings.kyber_mode,
        )
        payload = cipher.encrypt(data)
        private_key_b64 = encode_bytes(keypair["private_key"])
        payload["public_key"] = encode_bytes(keypair["public_key"])
    else:
        raise typer.BadParameter("Unsupported algorithm")

    encoded = encode_payload(
        payload,
        ["encrypted_key", "encapsulated_key", "ciphertext", "nonce", "associated_data"],
    )
    _write_json(payload_path, encoded)
    key_path.write_text(private_key_b64 + "\n", encoding="utf-8")
    typer.echo(f"Encrypted payload written to {payload_path}")
    typer.echo(f"Private key written to {key_path}")


@app.command()
def decrypt(algo: str, payload_file: str, key_file: str) -> None:
    """Decrypt a JSON payload file using the private key read from a key file."""
    algo = algo.lower()
    payload_data = json.loads(Path(payload_file).read_text(encoding="utf-8"))
    decoded_payload = decode_payload(
        payload_data,
        ["encrypted_key", "encapsulated_key", "ciphertext", "nonce", "associated_data"],
    )
    private_key_bytes = decode_bytes(Path(key_file).read_text(encoding="utf-8").strip())

    if algo == "rsa":
        cipher = RSAHybridCipher(private_key=private_key_bytes)
    elif algo == "kyber":
        cipher = KyberHybridCipher(private_key=private_key_bytes, kyber_mode=settings.kyber_mode)
    else:
        raise typer.BadParameter("Unsupported algorithm")

    try:
        plaintext = cipher.decrypt(decoded_payload)
    except Exception as exc:
        raise typer.Exit(code=1) from typer.echo(f"Decryption failed: {exc}", err=True)  # type: ignore[misc]

    typer.echo(encode_bytes(plaintext))


@app.command()
def benchmark(algo: str) -> None:
    """Run a benchmark workflow for the selected algorithm."""
    algo = algo.lower()
    results = run_benchmark(algo, sizes=settings.benchmark_sizes)
    typer.echo(json.dumps(results, indent=2))


@app.command()
def handshake(mode: str = "pqc") -> None:
    """Run a TLS-like handshake simulation."""
    mode = mode.lower()
    if mode == "classical":
        private_key, public_key = generate_rsa_keypair(key_size=settings.rsa_key_size)
        result = simulate_classical_handshake(
            server_public_key=serialize_public_key(public_key),
            server_private_key=serialize_private_key(private_key),
        )
    elif mode == "pqc":
        result = simulate_pqc_handshake()
    else:
        raise typer.BadParameter("Unsupported handshake mode")
    typer.echo(json.dumps({**result, "client_payload": encode_bytes(result["client_payload"]), "shared_secret": encode_bytes(result["shared_secret"])}, indent=2))


if __name__ == "__main__":
    app()
