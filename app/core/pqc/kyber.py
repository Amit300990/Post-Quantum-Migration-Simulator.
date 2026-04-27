from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Iterator

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.hkdf import HKDF


DEFAULT_KYBER_ALGORITHM = "Kyber768"


class KyberUnavailableError(RuntimeError):
    pass


def _load_oqs() -> object:
    try:
        import oqs  # type: ignore[import-not-found]
    except ImportError as exc:
        raise KyberUnavailableError(
            "liboqs-python is not available. Install liboqs and liboqs-python to enable Kyber."
        ) from exc
    return oqs


@contextmanager
def _kem(algorithm: str = DEFAULT_KYBER_ALGORITHM) -> Iterator[object]:
    oqs = _load_oqs()
    try:
        with oqs.KeyEncapsulation(algorithm) as kem:
            yield kem
    except Exception as exc:
        raise KyberUnavailableError(f"Unable to initialize OQS KEM '{algorithm}': {exc}") from exc


@dataclass(frozen=True)
class KyberKeyPair:
    algorithm: str
    public_key: bytes
    secret_key: bytes


@dataclass(frozen=True)
class KyberEncapsulation:
    ciphertext: bytes
    shared_secret: bytes


def generate_kyber_keypair(algorithm: str = DEFAULT_KYBER_ALGORITHM) -> KyberKeyPair:
    with _kem(algorithm) as kem:
        public_key = kem.generate_keypair()
        secret_key = kem.export_secret_key()
    return KyberKeyPair(algorithm=algorithm, public_key=public_key, secret_key=secret_key)


def encapsulate(public_key: bytes, algorithm: str = DEFAULT_KYBER_ALGORITHM) -> KyberEncapsulation:
    with _kem(algorithm) as kem:
        ciphertext, shared_secret = kem.encap_secret(public_key)
    return KyberEncapsulation(ciphertext=ciphertext, shared_secret=shared_secret)


def decapsulate(ciphertext: bytes, secret_key: bytes, algorithm: str = DEFAULT_KYBER_ALGORITHM) -> bytes:
    with _kem(algorithm) as kem:
        return kem.decap_secret(ciphertext, secret_key)


def derive_aes256_key(shared_secret: bytes, context: bytes = b"pq-migration-simulator:kyber-aes-gcm") -> bytes:
    return HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=None,
        info=context,
    ).derive(shared_secret)
