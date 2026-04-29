from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EncryptedPayload:
    metadata: dict[str, str | int | float]
    ciphertext: bytes
    nonce: bytes
    tag: bytes | None = None
    wrapped_key: bytes | None = None
    encapsulated_key: bytes | None = None


class CryptoProvider(Protocol):
    algorithm: str
    mode: str

    def encrypt(self, data: bytes) -> EncryptedPayload:
        ...

    def decrypt(self, payload: EncryptedPayload) -> bytes:
        ...
