from __future__ import annotations

from fastapi import APIRouter

from app.core.hsm import get_hsm_client
from app.core.negotiation import NegotiationParty, negotiate_algorithms
from app.core.profiles import list_profiles
from app.schemas.migration import (
    HsmGenerateKeyRequest,
    HsmKeyResponse,
    HsmOperationResponse,
    HsmWrapKeyRequest,
    NegotiationRequest,
    NegotiationResponse,
    NistProfileResponse,
)


router = APIRouter(tags=["migration"])


@router.get("/profiles", response_model=list[NistProfileResponse])
def get_profiles() -> list[dict[str, object]]:
    return [profile.to_dict() for profile in list_profiles()]


@router.post("/negotiate", response_model=NegotiationResponse)
def negotiate(request: NegotiationRequest) -> dict[str, object]:
    result = negotiate_algorithms(
        client=NegotiationParty(
            key_exchange_algorithms=request.client.key_exchange_algorithms,
            signature_algorithms=request.client.signature_algorithms,
        ),
        server=NegotiationParty(
            key_exchange_algorithms=request.server.key_exchange_algorithms,
            signature_algorithms=request.server.signature_algorithms,
        ),
        profile_name=request.profile,
    )
    return result.to_dict()


@router.post("/hsm/keys", response_model=HsmKeyResponse)
def generate_hsm_key(request: HsmGenerateKeyRequest) -> dict[str, object]:
    client = get_hsm_client(request.provider)
    key = client.generate_key(
        label=request.label,
        algorithm=request.algorithm,
        key_size=request.key_size,
        exportable=request.exportable,
    )
    return key.__dict__


@router.post("/hsm/wrap", response_model=HsmOperationResponse)
def wrap_key(request: HsmWrapKeyRequest) -> dict[str, object]:
    client = get_hsm_client(request.provider)
    key = client.generate_key(
        label=request.label,
        algorithm=request.algorithm,
        key_size=request.key_size,
        exportable=False,
    )
    result = client.wrap_key(key.key_id, bytes.fromhex(request.plaintext_key_hex))
    return result.to_dict()
