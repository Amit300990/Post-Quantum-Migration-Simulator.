from __future__ import annotations

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import oqs

DEFAULT_KYBER_MODE = "Kyber512"
AES_KEY_LENGTH = 32


def derive_aes_key(shared_secret: bytes, length: int = AES_KEY_LENGTH) -> bytes:
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=length,
        salt=None,
        info=b"pq-kyber-aes",
    )
    return hkdf.derive(shared_secret)


def generate_kyber_keypair(mode: str = DEFAULT_KYBER_MODE) -> dict[str, bytes]:
    with oqs.KeyEncapsulation(mode) as kem:
        public_key = kem.generate_keypair()
        private_key = kem.export_secret_key()
    return {"public_key": public_key, "private_key": private_key}


def kyber_encapsulate(public_key: bytes, mode: str = DEFAULT_KYBER_MODE) -> dict[str, bytes]:
    with oqs.KeyEncapsulation(mode) as kem:
        ciphertext, shared_secret = kem.encap_secret(public_key)
    return {"ciphertext": ciphertext, "shared_secret": shared_secret}


def kyber_decapsulate(ciphertext: bytes, private_key: bytes, mode: str = DEFAULT_KYBER_MODE) -> bytes:
    with oqs.KeyEncapsulation(mode) as kem:
        kem.import_secret_key(private_key)
        return kem.decap_secret(ciphertext)
