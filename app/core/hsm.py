from __future__ import annotations

import hashlib
import os
from dataclasses import asdict, dataclass
from typing import Protocol


@dataclass(frozen=True)
class HsmKeyRecord:
    key_id: str
    label: str
    algorithm: str
    key_size: int
    exportable: bool
    hsm_provider: str


@dataclass(frozen=True)
class HsmOperationResult:
    provider: str
    operation: str
    key_id: str
    algorithm: str
    payload_size: int
    result_size: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class HsmClient(Protocol):
    provider: str

    def list_keys(self) -> list[HsmKeyRecord]:
        ...

    def generate_key(self, label: str, algorithm: str, key_size: int, exportable: bool = False) -> HsmKeyRecord:
        ...

    def wrap_key(self, key_id: str, plaintext_key: bytes) -> HsmOperationResult:
        ...


class SoftwareHsmClient:
    provider = "software-hsm-simulator"

    def __init__(self) -> None:
        self._keys: dict[str, HsmKeyRecord] = {}

    def list_keys(self) -> list[HsmKeyRecord]:
        return list(self._keys.values())

    def generate_key(self, label: str, algorithm: str, key_size: int, exportable: bool = False) -> HsmKeyRecord:
        key_id = hashlib.sha256(f"{label}:{algorithm}:{os.urandom(16).hex()}".encode("utf-8")).hexdigest()[:24]
        record = HsmKeyRecord(
            key_id=key_id,
            label=label,
            algorithm=algorithm.lower(),
            key_size=key_size,
            exportable=exportable,
            hsm_provider=self.provider,
        )
        self._keys[key_id] = record
        return record

    def wrap_key(self, key_id: str, plaintext_key: bytes) -> HsmOperationResult:
        record = self._keys.get(key_id)
        if record is None:
            raise KeyError(f"Unknown HSM key id: {key_id}")
        digest = hashlib.sha256(key_id.encode("utf-8") + plaintext_key).digest()
        return HsmOperationResult(
            provider=self.provider,
            operation="wrap_key",
            key_id=key_id,
            algorithm=record.algorithm,
            payload_size=len(plaintext_key),
            result_size=len(digest),
        )


def get_hsm_client(provider: str = "software") -> HsmClient:
    normalized = provider.lower()
    if normalized in {"software", "simulator", "software-hsm"}:
        return SoftwareHsmClient()
    raise ValueError(f"Unsupported HSM provider: {provider}")
