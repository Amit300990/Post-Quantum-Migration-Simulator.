from __future__ import annotations

import os
from dataclasses import dataclass

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


AES_256_KEY_BYTES = 32
AES_GCM_NONCE_BYTES = 12


@dataclass(frozen=True)
class AesGcmCiphertext:
    nonce: bytes
    ciphertext: bytes
    tag: bytes

    @property
    def combined(self) -> bytes:
        return self.ciphertext + self.tag


def generate_aes256_key() -> bytes:
    return os.urandom(AES_256_KEY_BYTES)


def encrypt_aes_gcm(data: bytes, key: bytes, associated_data: bytes | None = None) -> AesGcmCiphertext:
    if len(key) != AES_256_KEY_BYTES:
        raise ValueError("AES-256-GCM requires a 32-byte key.")

    nonce = os.urandom(AES_GCM_NONCE_BYTES)
    encrypted = AESGCM(key).encrypt(nonce, data, associated_data)
    return AesGcmCiphertext(
        nonce=nonce,
        ciphertext=encrypted[:-16],
        tag=encrypted[-16:],
    )


def decrypt_aes_gcm(payload: AesGcmCiphertext, key: bytes, associated_data: bytes | None = None) -> bytes:
    if len(key) != AES_256_KEY_BYTES:
        raise ValueError("AES-256-GCM requires a 32-byte key.")

    return AESGCM(key).decrypt(payload.nonce, payload.combined, associated_data)
