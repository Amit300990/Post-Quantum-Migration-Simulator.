from __future__ import annotations

from pydantic import BaseModel


class NistProfileResponse(BaseModel):
    name: str
    description: str
    allowed_kems: list[str]
    allowed_signatures: list[str]
    allowed_classical_key_exchange: list[str]
    allowed_classical_signatures: list[str]
    preferred_key_exchange_order: list[str]
    min_rsa_bits: int
    allow_classical_only: bool
    require_hybrid: bool
    require_pqc: bool
    target_state: str
    retirement_guidance: list[str]


class NegotiationPartyRequest(BaseModel):
    key_exchange_algorithms: list[str]
    signature_algorithms: list[str]


class NegotiationRequest(BaseModel):
    profile: str = "hybrid_transition"
    client: NegotiationPartyRequest
    server: NegotiationPartyRequest


class NegotiationPartyResponse(BaseModel):
    key_exchange_algorithms: list[str]
    signature_algorithms: list[str]


class NegotiationResponse(BaseModel):
    status: str
    profile: str
    selected_key_exchange: str | None
    selected_signature: str | None
    protocol_mode: str | None
    failure_reason: str | None
    client_supported: NegotiationPartyResponse
    server_supported: NegotiationPartyResponse


class HsmKeyResponse(BaseModel):
    key_id: str
    label: str
    algorithm: str
    key_size: int
    exportable: bool
    hsm_provider: str


class HsmGenerateKeyRequest(BaseModel):
    provider: str = "software"
    label: str
    algorithm: str = "ml-kem-768"
    key_size: int = 256
    exportable: bool = False


class HsmWrapKeyRequest(BaseModel):
    provider: str = "software"
    label: str = "migration-wrapping-key"
    algorithm: str = "rsa-3072"
    key_size: int = 3072
    plaintext_key_hex: str


class HsmOperationResponse(BaseModel):
    provider: str
    operation: str
    key_id: str
    algorithm: str
    payload_size: int
    result_size: int
