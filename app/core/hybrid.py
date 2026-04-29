from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any

from app.core.classical.aes import decrypt_aes_gcm, encrypt_aes_gcm, generate_aes_key
from app.core.classical.rsa import load_private_key, load_public_key, rsa_decrypt, rsa_encrypt
from app.core.pqc.kyber import derive_aes_key, kyber_decapsulate, kyber_encapsulate


class CryptoEngine(ABC):
    @abstractmethod
    def encrypt(self, data: bytes) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, payload: dict[str, Any]) -> bytes:
        raise NotImplementedError


class RSAHybridCipher(CryptoEngine):
    def __init__(self, public_key: bytes | None = None, private_key: bytes | None = None) -> None:
        self.public_key = load_public_key(public_key) if public_key else None
        self.private_key = load_private_key(private_key) if private_key else None
        self.algorithm = "rsa-2048+aes-256-gcm"
        self.mode = "classical"

    def encrypt(self, data: bytes) -> dict[str, Any]:
        session_key = generate_aes_key()
        encrypted_key = rsa_encrypt(self.public_key, session_key)
        cipher_payload = encrypt_aes_gcm(data, session_key)

        return {
            "algorithm": self.algorithm,
            "mode": self.mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "key_size": 2048,
            "encrypted_key": encrypted_key,
            "ciphertext": cipher_payload["ciphertext"],
            "nonce": cipher_payload["nonce"],
            "associated_data": cipher_payload["associated_data"],
        }

    def decrypt(self, payload: dict[str, Any]) -> bytes:
        if self.private_key is None:
            raise ValueError("Private key required for decryption")
        session_key = rsa_decrypt(self.private_key, payload["encrypted_key"])
        return decrypt_aes_gcm(payload, session_key)


class KyberHybridCipher(CryptoEngine):
    def __init__(self, public_key: bytes | None = None, private_key: bytes | None = None, kyber_mode: str = "Kyber512") -> None:
        self.public_key = public_key
        self.private_key = private_key
        self.kyber_mode = kyber_mode
        self.algorithm = "kyber+aes-256-gcm"
        self.mode = "pqc"

    def encrypt(self, data: bytes) -> dict[str, Any]:
        encapsulation = kyber_encapsulate(self.public_key, self.kyber_mode)
        session_key = derive_aes_key(encapsulation["shared_secret"])
        cipher_payload = encrypt_aes_gcm(data, session_key)

        return {
            "algorithm": self.algorithm,
            "mode": self.mode,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "key_size": len(self.public_key) * 8,
            "encapsulated_key": encapsulation["ciphertext"],
            "ciphertext": cipher_payload["ciphertext"],
            "nonce": cipher_payload["nonce"],
            "associated_data": cipher_payload["associated_data"],
        }

    def decrypt(self, payload: dict[str, Any]) -> bytes:
        if self.private_key is None:
            raise ValueError("Private key required for decryption")
        shared_secret = kyber_decapsulate(payload["encapsulated_key"], self.private_key, self.kyber_mode)
        session_key = derive_aes_key(shared_secret)
        return decrypt_aes_gcm(payload, session_key)
