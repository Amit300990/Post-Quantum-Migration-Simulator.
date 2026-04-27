from __future__ import annotations

import base64
import json
from dataclasses import asdict
from datetime import datetime, timezone
from typing import Any

from app.core.classical.aes import AesGcmCiphertext, decrypt_aes_gcm, encrypt_aes_gcm, generate_aes256_key
from app.core.classical.rsa import RsaKeyPair, decrypt_with_rsa_oaep, encrypt_with_rsa_oaep, generate_rsa_keypair
from app.core.interfaces import EncryptedPayload
from app.core.pqc.kyber import (
    DEFAULT_KYBER_ALGORITHM,
    KyberKeyPair,
    decapsulate,
    derive_aes256_key,
    encapsulate,
    generate_kyber_keypair,
)
from app.utils.config import get_settings


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


class RsaHybridCrypto:
    algorithm = "RSA-2048 + AES-256-GCM"
    mode = "classical"

    def __init__(self, key_pair: RsaKeyPair | None = None) -> None:
        settings = get_settings()
        self.key_pair = key_pair or generate_rsa_keypair(settings.rsa_key_size)

    def encrypt(self, data: bytes) -> EncryptedPayload:
        aes_key = generate_aes256_key()
        aes_payload = encrypt_aes_gcm(data, aes_key)
        wrapped_key = encrypt_with_rsa_oaep(self.key_pair.public_key, aes_key)
        return EncryptedPayload(
            metadata={
                "algorithm": self.algorithm,
                "key_size": self.key_pair.public_key.key_size,
                "timestamp": _utc_timestamp(),
                "mode": self.mode,
            },
            ciphertext=aes_payload.ciphertext,
            nonce=aes_payload.nonce,
            tag=aes_payload.tag,
            wrapped_key=wrapped_key,
        )

    def decrypt(self, payload: EncryptedPayload) -> bytes:
        if payload.wrapped_key is None or payload.tag is None:
            raise ValueError("RSA hybrid payload requires wrapped_key and tag.")
        aes_key = decrypt_with_rsa_oaep(self.key_pair.private_key, payload.wrapped_key)
        return decrypt_aes_gcm(
            AesGcmCiphertext(nonce=payload.nonce, ciphertext=payload.ciphertext, tag=payload.tag),
            aes_key,
        )


class KyberHybridCrypto:
    algorithm = f"{DEFAULT_KYBER_ALGORITHM} + AES-256-GCM"
    mode = "pqc"

    def __init__(self, key_pair: KyberKeyPair | None = None, algorithm: str = DEFAULT_KYBER_ALGORITHM) -> None:
        self.kyber_algorithm = algorithm
        self.key_pair = key_pair or generate_kyber_keypair(algorithm)
        self.algorithm = f"{algorithm} + AES-256-GCM"

    def encrypt(self, data: bytes) -> EncryptedPayload:
        encapsulation = encapsulate(self.key_pair.public_key, self.kyber_algorithm)
        aes_key = derive_aes256_key(encapsulation.shared_secret)
        aes_payload = encrypt_aes_gcm(data, aes_key)
        return EncryptedPayload(
            metadata={
                "algorithm": self.algorithm,
                "key_size": len(self.key_pair.public_key),
                "timestamp": _utc_timestamp(),
                "mode": self.mode,
            },
            ciphertext=aes_payload.ciphertext,
            nonce=aes_payload.nonce,
            tag=aes_payload.tag,
            encapsulated_key=encapsulation.ciphertext,
        )

    def decrypt(self, payload: EncryptedPayload) -> bytes:
        if payload.encapsulated_key is None or payload.tag is None:
            raise ValueError("Kyber hybrid payload requires encapsulated_key and tag.")
        shared_secret = decapsulate(payload.encapsulated_key, self.key_pair.secret_key, self.kyber_algorithm)
        aes_key = derive_aes256_key(shared_secret)
        return decrypt_aes_gcm(
            AesGcmCiphertext(nonce=payload.nonce, ciphertext=payload.ciphertext, tag=payload.tag),
            aes_key,
        )


def payload_to_bytes(payload: EncryptedPayload) -> bytes:
    serializable: dict[str, Any] = asdict(payload)
    for field in ("ciphertext", "nonce", "tag", "wrapped_key", "encapsulated_key"):
        value = serializable[field]
        serializable[field] = base64.b64encode(value).decode("ascii") if value is not None else None
    return json.dumps(serializable, separators=(",", ":")).encode("utf-8")


def payload_from_bytes(data: bytes) -> EncryptedPayload:
    raw = json.loads(data.decode("utf-8"))
    decoded: dict[str, Any] = {"metadata": raw["metadata"]}
    for field in ("ciphertext", "nonce", "tag", "wrapped_key", "encapsulated_key"):
        value = raw.get(field)
        decoded[field] = base64.b64decode(value) if value is not None else None
    return EncryptedPayload(**decoded)


def provider_for_algorithm(algorithm: str) -> RsaHybridCrypto | KyberHybridCrypto:
    normalized = algorithm.lower()
    if normalized in {"rsa", "classical", "rsa-2048"}:
        return RsaHybridCrypto()
    if normalized in {"kyber", "pqc", DEFAULT_KYBER_ALGORITHM.lower()}:
        return KyberHybridCrypto(algorithm=get_settings().kyber_algorithm)
    raise ValueError(f"Unsupported algorithm: {algorithm}")
