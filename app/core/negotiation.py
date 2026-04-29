from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

from app.core.profiles import NistPqcMigrationProfile, get_profile


NegotiationStatus = Literal["negotiated", "failed"]


@dataclass(frozen=True)
class NegotiationParty:
    key_exchange_algorithms: list[str]
    signature_algorithms: list[str]


@dataclass(frozen=True)
class NegotiationResult:
    status: NegotiationStatus
    profile: str
    selected_key_exchange: str | None
    selected_signature: str | None
    protocol_mode: str | None
    failure_reason: str | None
    client_supported: NegotiationParty
    server_supported: NegotiationParty

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _normalize(algorithms: list[str]) -> list[str]:
    return [algorithm.lower() for algorithm in algorithms]


def _is_hybrid(algorithm: str) -> bool:
    return "+" in algorithm


def _is_pqc(algorithm: str) -> bool:
    normalized = algorithm.lower()
    return normalized.startswith("ml-kem") or normalized.startswith("kyber")


def _protocol_mode(key_exchange: str) -> str:
    if _is_hybrid(key_exchange):
        return "hybrid"
    if _is_pqc(key_exchange):
        return "pqc"
    return "classical"


def _profile_key_exchange_candidates(profile: NistPqcMigrationProfile) -> list[str]:
    candidates = list(profile.preferred_key_exchange_order)
    candidates.extend(profile.allowed_kems)
    candidates.extend(profile.allowed_classical_key_exchange)
    return list(dict.fromkeys(_normalize(candidates)))


def _profile_signature_candidates(profile: NistPqcMigrationProfile) -> list[str]:
    candidates = profile.allowed_signatures + profile.allowed_classical_signatures
    return list(dict.fromkeys(_normalize(candidates)))


def negotiate_algorithms(
    client: NegotiationParty,
    server: NegotiationParty,
    profile_name: str = "hybrid_transition",
) -> NegotiationResult:
    profile = get_profile(profile_name)
    client_kex = set(_normalize(client.key_exchange_algorithms))
    server_kex = set(_normalize(server.key_exchange_algorithms))
    client_sig = set(_normalize(client.signature_algorithms))
    server_sig = set(_normalize(server.signature_algorithms))

    selected_kex = next(
        (
            candidate
            for candidate in _profile_key_exchange_candidates(profile)
            if candidate in client_kex and candidate in server_kex
        ),
        None,
    )
    selected_sig = next(
        (
            candidate
            for candidate in _profile_signature_candidates(profile)
            if candidate in client_sig and candidate in server_sig
        ),
        None,
    )

    if selected_kex is None:
        return NegotiationResult(
            status="failed",
            profile=profile.name,
            selected_key_exchange=None,
            selected_signature=None,
            protocol_mode=None,
            failure_reason="No mutually supported key exchange algorithm is allowed by the selected profile.",
            client_supported=client,
            server_supported=server,
        )

    mode = _protocol_mode(selected_kex)
    if profile.require_hybrid and mode != "hybrid":
        return NegotiationResult(
            status="failed",
            profile=profile.name,
            selected_key_exchange=selected_kex,
            selected_signature=selected_sig,
            protocol_mode=mode,
            failure_reason="Profile requires hybrid key exchange.",
            client_supported=client,
            server_supported=server,
        )
    if profile.require_pqc and mode == "classical":
        return NegotiationResult(
            status="failed",
            profile=profile.name,
            selected_key_exchange=selected_kex,
            selected_signature=selected_sig,
            protocol_mode=mode,
            failure_reason="Profile requires PQC or hybrid key exchange.",
            client_supported=client,
            server_supported=server,
        )
    if selected_sig is None:
        return NegotiationResult(
            status="failed",
            profile=profile.name,
            selected_key_exchange=selected_kex,
            selected_signature=None,
            protocol_mode=mode,
            failure_reason="No mutually supported signature algorithm is allowed by the selected profile.",
            client_supported=client,
            server_supported=server,
        )

    return NegotiationResult(
        status="negotiated",
        profile=profile.name,
        selected_key_exchange=selected_kex,
        selected_signature=selected_sig,
        protocol_mode=mode,
        failure_reason=None,
        client_supported=client,
        server_supported=server,
    )
