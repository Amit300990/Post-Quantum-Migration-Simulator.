from __future__ import annotations

import os
import time
from dataclasses import dataclass

from app.core.classical.rsa import decrypt_with_rsa_oaep, encrypt_with_rsa_oaep, generate_rsa_keypair
from app.core.pqc.kyber import (
    DEFAULT_KYBER_ALGORITHM,
    decapsulate,
    encapsulate,
    generate_kyber_keypair,
)
from app.utils.config import get_settings


PRE_MASTER_SECRET_BYTES = 48


@dataclass(frozen=True)
class HandshakeResult:
    mode: str
    algorithm: str
    latency_ms: float
    payload_size: int
    shared_secret_size: int
    success: bool


def simulate_classical_handshake() -> HandshakeResult:
    settings = get_settings()
    key_pair = generate_rsa_keypair(settings.rsa_key_size)
    pre_master_secret = os.urandom(PRE_MASTER_SECRET_BYTES)

    start = time.perf_counter()
    encrypted_secret = encrypt_with_rsa_oaep(key_pair.public_key, pre_master_secret)
    server_secret = decrypt_with_rsa_oaep(key_pair.private_key, encrypted_secret)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return HandshakeResult(
        mode="classical",
        algorithm=f"RSA-{settings.rsa_key_size}",
        latency_ms=elapsed_ms,
        payload_size=len(encrypted_secret),
        shared_secret_size=len(server_secret),
        success=server_secret == pre_master_secret,
    )


def simulate_pqc_handshake(algorithm: str = DEFAULT_KYBER_ALGORITHM) -> HandshakeResult:
    key_pair = generate_kyber_keypair(algorithm)

    start = time.perf_counter()
    client_result = encapsulate(key_pair.public_key, algorithm)
    server_secret = decapsulate(client_result.ciphertext, key_pair.secret_key, algorithm)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return HandshakeResult(
        mode="pqc",
        algorithm=algorithm,
        latency_ms=elapsed_ms,
        payload_size=len(client_result.ciphertext),
        shared_secret_size=len(server_secret),
        success=server_secret == client_result.shared_secret,
    )


def simulate_handshake(mode: str) -> HandshakeResult:
    normalized = mode.lower()
    if normalized in {"rsa", "classical"}:
        return simulate_classical_handshake()
    if normalized in {"kyber", "pqc"}:
        return simulate_pqc_handshake(get_settings().kyber_algorithm)
    raise ValueError(f"Unsupported handshake mode: {mode}")
