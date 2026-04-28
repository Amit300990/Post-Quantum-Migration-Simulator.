from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Any

from app.core.classical.rsa import generate_rsa_keypair, serialize_private_key, serialize_public_key
from app.core.handshake import simulate_classical_handshake, simulate_pqc_handshake
from app.db.database import get_db
from app.db.models import HandshakeResult
from app.utils.logger import logger
from app.utils.serialization import encode_bytes

router = APIRouter(tags=["handshake"])


@router.post("/handshake")
def handshake(mode: str = "pqc", db: Session = Depends(get_db)) -> dict[str, Any]:
    mode = mode.lower()
    if mode == "classical":
        private_key, public_key = generate_rsa_keypair()
        response = simulate_classical_handshake(
            server_public_key=serialize_public_key(public_key),
            server_private_key=serialize_private_key(private_key),
        )
    elif mode == "pqc":
        response = simulate_pqc_handshake()
    else:
        raise HTTPException(status_code=400, detail="Unsupported handshake mode")

    record = HandshakeResult(
        algorithm=response["algorithm"],
        mode=response["mode"],
        handshake_latency_ms=response["handshake_latency_ms"],
        payload_size=response["payload_size"],
        shared_secret_size=response["shared_secret_size"],
    )
    db.add(record)
    db.commit()

    encoded_response: dict[str, Any] = {
        **response,
        "client_payload": encode_bytes(response["client_payload"]),
        "shared_secret": encode_bytes(response["shared_secret"]),
    }
    logger.info("Simulated %s handshake", mode)
    return encoded_response
