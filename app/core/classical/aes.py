from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AES_KEY_SIZE = 32
AES_GCM_NONCE_SIZE = 12


def generate_aes_key(key_size: int = AES_KEY_SIZE) -> bytes:
    return os.urandom(key_size)


def encrypt_aes_gcm(plaintext: bytes, key: bytes, associated_data: bytes | None = None) -> dict[str, Any]:
    nonce = os.urandom(AES_GCM_NONCE_SIZE)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
    return {
        "ciphertext": ciphertext,
        "nonce": nonce,
        "associated_data": associated_data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def decrypt_aes_gcm(payload: dict[str, Any], key: bytes, associated_data: bytes | None = None) -> bytes:
    aesgcm = AESGCM(key)
    nonce = payload["nonce"]
    ciphertext = payload["ciphertext"]
    return aesgcm.decrypt(nonce, ciphertext, associated_data)
