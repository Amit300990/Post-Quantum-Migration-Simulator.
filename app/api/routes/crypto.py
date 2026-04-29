from __future__ import annotations

from typing import Any

from fastapi import APIRouter, File, HTTPException, Request, UploadFile

from app.core.classical.rsa import generate_rsa_keypair, serialize_private_key, serialize_public_key
from app.core.pqc.kyber import generate_kyber_keypair
from app.core.hybrid import RSAHybridCipher, KyberHybridCipher
from app.schemas.crypto import DecryptResponse, EncryptResponse
from app.utils.config import settings
from app.utils.limiter import limiter
from app.utils.logger import logger
from app.utils.serialization import encode_bytes, encode_payload, decode_bytes, decode_payload

router = APIRouter(tags=["crypto"])

ALLOWED_ALGORITHMS = {"rsa", "kyber"}


@router.get("/algorithms")
def list_algorithms() -> dict[str, Any]:
    return {
        "algorithms": list(settings.algorithms_enabled),
        "mode": "crypto",
    }


@router.post("/encrypt", response_model=EncryptResponse)
@limiter.limit("20/minute")
async def encrypt_file(request: Request, algorithm: str, file: UploadFile = File(...)) -> dict[str, Any]:
    algorithm = algorithm.lower()
    if algorithm not in ALLOWED_ALGORITHMS:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file upload")
    if len(data) > 50 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="File too large (max 50 MB)")

    if algorithm == "rsa":
        private_key, public_key = generate_rsa_keypair(key_size=settings.rsa_key_size)
        cipher = RSAHybridCipher(
            public_key=serialize_public_key(public_key),
            private_key=serialize_private_key(private_key),
        )
        payload = cipher.encrypt(data)
        payload["private_key"] = encode_bytes(serialize_private_key(private_key))
        payload["public_key"] = encode_bytes(serialize_public_key(public_key))
    else:
        keypair = generate_kyber_keypair(mode=settings.kyber_mode)
        cipher = KyberHybridCipher(
            public_key=keypair["public_key"],
            private_key=keypair["private_key"],
            kyber_mode=settings.kyber_mode,
        )
        payload = cipher.encrypt(data)
        payload["private_key"] = encode_bytes(keypair["private_key"])
        payload["public_key"] = encode_bytes(keypair["public_key"])

    encoded = encode_payload(
        payload,
        ["encrypted_key", "encapsulated_key", "ciphertext", "nonce", "associated_data"],
    )
    logger.info("Encrypted file with %s", algorithm)
    return encoded


@router.post("/decrypt", response_model=DecryptResponse)
def decrypt_file(body: dict[str, Any]) -> dict[str, Any]:
    algorithm = body.get("algorithm", "").lower()
    if algorithm not in ALLOWED_ALGORITHMS:
        raise HTTPException(status_code=400, detail="Unsupported algorithm")

    private_key = body.get("private_key")
    payload = body.get("payload")
    if not private_key or not payload:
        raise HTTPException(status_code=400, detail="Missing private_key or payload")

    decoded_payload = decode_payload(
        payload,
        ["encrypted_key", "encapsulated_key", "ciphertext", "nonce", "associated_data"],
    )
    private_key_bytes = decode_bytes(private_key)

    if algorithm == "rsa":
        cipher = RSAHybridCipher(private_key=private_key_bytes)
    else:
        cipher = KyberHybridCipher(private_key=private_key_bytes, kyber_mode=settings.kyber_mode)

    try:
        plaintext = cipher.decrypt(decoded_payload)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Decryption failed: {exc}") from exc

    logger.info("Decrypted payload with %s", algorithm)
    return {
        "algorithm": algorithm,
        "plaintext": encode_bytes(plaintext),
        "message": "Use base64 decode to recover original bytes.",
    }
