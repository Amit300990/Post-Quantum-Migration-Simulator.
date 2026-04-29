import pytest

from app.core.classical.rsa import generate_rsa_keypair, serialize_private_key, serialize_public_key
from app.core.hybrid import RSAHybridCipher, KyberHybridCipher
from app.core.pqc.kyber import generate_kyber_keypair


def test_rsa_hybrid_encrypt_decrypt() -> None:
    private_key, public_key = generate_rsa_keypair()
    cipher = RSAHybridCipher(
        public_key=serialize_public_key(public_key),
        private_key=serialize_private_key(private_key),
    )
    message = b"secure migration simulator"
    payload = cipher.encrypt(message)
    plaintext = cipher.decrypt(payload)
    assert plaintext == message


def test_kyber_hybrid_encrypt_decrypt() -> None:
    keypair = generate_kyber_keypair()
    cipher = KyberHybridCipher(
        public_key=keypair["public_key"],
        private_key=keypair["private_key"],
    )
    message = b"post-quantum validation"
    payload = cipher.encrypt(message)
    plaintext = cipher.decrypt(payload)
    assert plaintext == message


def test_rsa_missing_private_key_raises() -> None:
    _, public_key = generate_rsa_keypair()
    cipher = RSAHybridCipher(public_key=serialize_public_key(public_key))
    payload = cipher.encrypt(b"test")
    with pytest.raises(ValueError, match="Private key required"):
        cipher.decrypt(payload)


def test_kyber_missing_private_key_raises() -> None:
    keypair = generate_kyber_keypair()
    cipher = KyberHybridCipher(public_key=keypair["public_key"])
    payload = cipher.encrypt(b"test")
    with pytest.raises(ValueError, match="Private key required"):
        cipher.decrypt(payload)


def test_rsa_decrypt_wrong_key_raises() -> None:
    private_key1, public_key1 = generate_rsa_keypair()
    private_key2, _ = generate_rsa_keypair()
    cipher_enc = RSAHybridCipher(public_key=serialize_public_key(public_key1))
    cipher_dec = RSAHybridCipher(private_key=serialize_private_key(private_key2))
    payload = cipher_enc.encrypt(b"sensitive data")
    with pytest.raises(Exception):
        cipher_dec.decrypt(payload)


def test_kyber_tampered_ciphertext_raises() -> None:
    keypair = generate_kyber_keypair()
    cipher = KyberHybridCipher(
        public_key=keypair["public_key"],
        private_key=keypair["private_key"],
    )
    payload = cipher.encrypt(b"sensitive data")
    tampered = dict(payload)
    tampered["ciphertext"] = bytes(b ^ 0xFF for b in payload["ciphertext"])
    with pytest.raises(Exception):
        cipher.decrypt(tampered)


def test_rsa_empty_plaintext_roundtrip() -> None:
    private_key, public_key = generate_rsa_keypair()
    cipher = RSAHybridCipher(
        public_key=serialize_public_key(public_key),
        private_key=serialize_private_key(private_key),
    )
    payload = cipher.encrypt(b"")
    assert cipher.decrypt(payload) == b""


def test_kyber_large_plaintext_roundtrip() -> None:
    import os
    keypair = generate_kyber_keypair()
    cipher = KyberHybridCipher(
        public_key=keypair["public_key"],
        private_key=keypair["private_key"],
    )
    message = os.urandom(1024 * 1024)
    payload = cipher.encrypt(message)
    assert cipher.decrypt(payload) == message
