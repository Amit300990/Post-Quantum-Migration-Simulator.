from __future__ import annotations

import base64
from typing import Any


def encode_bytes(value: bytes) -> str:
    return base64.b64encode(value).decode("utf-8")


def decode_bytes(value: str) -> bytes:
    return base64.b64decode(value.encode("utf-8"))


def encode_payload(payload: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    encoded = payload.copy()
    for field in fields:
        if field in encoded and isinstance(encoded[field], (bytes, bytearray)):
            encoded[field] = encode_bytes(bytes(encoded[field]))
    return encoded


def decode_payload(payload: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    decoded = payload.copy()
    for field in fields:
        if field in decoded and isinstance(decoded[field], str):
            decoded[field] = decode_bytes(decoded[field])
    return decoded
