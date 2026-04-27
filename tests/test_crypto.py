from __future__ import annotations

import pytest

cryptography = pytest.importorskip("cryptography")

from app.core.classical.aes import AesGcmCiphertext, decrypt_aes_gcm, encrypt_aes_gcm, generate_aes256_key
from app.core.hybrid import RsaHybridCrypto, payload_from_bytes, payload_to_bytes, provider_for_algorithm
from app.core.pqc.kyber import KyberUnavailableError, derive_aes256_key, generate_kyber_keypair


def test_aes_gcm_round_trip_preserves_plaintext() -> None:
    key = generate_aes256_key()
    plaintext = b"post-quantum migration simulator test payload"

    payload = encrypt_aes_gcm(plaintext, key, associated_data=b"context")
    decrypted = decrypt_aes_gcm(payload, key, associated_data=b"context")

    assert decrypted == plaintext
    assert len(payload.nonce) == 12
    assert len(payload.tag) == 16


def test_aes_gcm_rejects_invalid_key_size() -> None:
    with pytest.raises(ValueError, match="32-byte key"):
        encrypt_aes_gcm(b"payload", b"short")


def test_aes_gcm_detects_tampered_ciphertext() -> None:
    key = generate_aes256_key()
    payload = encrypt_aes_gcm(b"authenticated plaintext", key)
    tampered = AesGcmCiphertext(
        nonce=payload.nonce,
        ciphertext=payload.ciphertext[:-1] + bytes([payload.ciphertext[-1] ^ 1]),
        tag=payload.tag,
    )

    with pytest.raises(Exception):
        decrypt_aes_gcm(tampered, key)


def test_rsa_hybrid_round_trip_and_metadata() -> None:
    provider = RsaHybridCrypto()
    plaintext = b"hybrid RSA AES payload"

    encrypted = provider.encrypt(plaintext)
    decrypted = provider.decrypt(encrypted)

    assert decrypted == plaintext
    assert encrypted.metadata["mode"] == "classical"
    assert encrypted.metadata["algorithm"] == "RSA-2048 + AES-256-GCM"
    assert encrypted.metadata["key_size"] >= 2048
    assert encrypted.wrapped_key is not None


def test_rsa_hybrid_payload_serialization_round_trip() -> None:
    provider = RsaHybridCrypto()
    encrypted = provider.encrypt(b"serialized payload")

    encoded = payload_to_bytes(encrypted)
    decoded = payload_from_bytes(encoded)

    assert provider.decrypt(decoded) == b"serialized payload"
    assert decoded.metadata == encrypted.metadata


def test_rsa_hybrid_rejects_missing_wrapped_key() -> None:
    provider = RsaHybridCrypto()
    encrypted = provider.encrypt(b"payload")
    invalid_payload = type(encrypted)(
        metadata=encrypted.metadata,
        ciphertext=encrypted.ciphertext,
        nonce=encrypted.nonce,
        tag=encrypted.tag,
        wrapped_key=None,
        encapsulated_key=None,
    )

    with pytest.raises(ValueError, match="wrapped_key"):
        provider.decrypt(invalid_payload)


def test_provider_for_algorithm_rejects_unknown_algorithm() -> None:
    with pytest.raises(ValueError, match="Unsupported algorithm"):
        provider_for_algorithm("rot13")


def test_kyber_keygen_is_skip_safe_when_oqs_unavailable() -> None:
    try:
        key_pair = generate_kyber_keypair()
    except KyberUnavailableError:
        pytest.skip("liboqs-python is not available in this environment")

    assert key_pair.public_key
    assert key_pair.secret_key


def test_kyber_shared_secret_derivation_is_reproducible() -> None:
    secret = b"shared-secret-material"

    first = derive_aes256_key(secret)
    second = derive_aes256_key(secret)

    assert first == second
    assert len(first) == 32
