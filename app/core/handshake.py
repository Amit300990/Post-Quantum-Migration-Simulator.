from __future__ import annotations

import time
from typing import Any
from datetime import datetime, timezone

from app.core.classical.rsa import generate_rsa_keypair, load_private_key, load_public_key, rsa_decrypt, rsa_encrypt
from app.core.pqc.kyber import generate_kyber_keypair, kyber_decapsulate, kyber_encapsulate


def simulate_classical_handshake(server_public_key: bytes, server_private_key: bytes) -> dict[str, Any]:
    pre_master_secret = b"PREMASTER_SECRET_" + datetime.now(timezone.utc).isoformat().encode("utf-8")
    public_key = load_public_key(server_public_key)
    private_key = load_private_key(server_private_key)
    start = time.perf_counter()
    client_payload = rsa_encrypt(public_key, pre_master_secret)
    server_secret = rsa_decrypt(private_key, client_payload)
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "mode": "classical",
        "algorithm": "rsa-key-exchange",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "handshake_latency_ms": elapsed_ms,
        "payload_size": len(client_payload),
        "shared_secret_size": len(server_secret),
        "shared_secret": server_secret,
        "client_payload": client_payload,
    }


def simulate_pqc_handshake() -> dict[str, Any]:
    keypair = generate_kyber_keypair()
    start = time.perf_counter()
    encapsulation = kyber_encapsulate(keypair["public_key"])
    server_secret = kyber_decapsulate(encapsulation["ciphertext"], keypair["private_key"])
    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "mode": "pqc",
        "algorithm": "kyber-kem",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "handshake_latency_ms": elapsed_ms,
        "payload_size": len(encapsulation["ciphertext"]),
        "shared_secret_size": len(server_secret),
        "shared_secret": server_secret,
        "client_payload": encapsulation["ciphertext"],
    }
