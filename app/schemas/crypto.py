from __future__ import annotations

from pydantic import BaseModel


class EncryptResponse(BaseModel):
    algorithm: str
    mode: str
    timestamp: str
    key_size: int
    ciphertext: str
    nonce: str
    associated_data: str | None = None
    encrypted_key: str | None = None
    encapsulated_key: str | None = None
    private_key: str
    public_key: str


class DecryptResponse(BaseModel):
    algorithm: str
    plaintext: str
    message: str
