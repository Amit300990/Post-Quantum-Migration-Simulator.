from __future__ import annotations

from dataclasses import dataclass

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey, RSAPublicKey


@dataclass(frozen=True)
class RsaKeyPair:
    private_key: RSAPrivateKey
    public_key: RSAPublicKey

    @property
    def public_key_pem(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    @property
    def private_key_pem(self) -> bytes:
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )


def generate_rsa_keypair(key_size: int = 2048) -> RsaKeyPair:
    if key_size < 2048:
        raise ValueError("RSA key size must be at least 2048 bits.")

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    return RsaKeyPair(private_key=private_key, public_key=private_key.public_key())


def encrypt_with_rsa_oaep(public_key: RSAPublicKey, data: bytes) -> bytes:
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def decrypt_with_rsa_oaep(private_key: RSAPrivateKey, ciphertext: bytes) -> bytes:
    return private_key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )


def load_public_key_pem(data: bytes) -> RSAPublicKey:
    key = serialization.load_pem_public_key(data)
    if not isinstance(key, RSAPublicKey):
        raise TypeError("PEM data does not contain an RSA public key.")
    return key


def load_private_key_pem(data: bytes) -> RSAPrivateKey:
    key = serialization.load_pem_private_key(data, password=None)
    if not isinstance(key, RSAPrivateKey):
        raise TypeError("PEM data does not contain an RSA private key.")
    return key
