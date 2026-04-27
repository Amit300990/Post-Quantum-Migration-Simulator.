from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal


MigrationProfileName = Literal["baseline", "hybrid_transition", "pqc_preferred", "strict_pqc"]


@dataclass(frozen=True)
class NistPqcMigrationProfile:
    name: MigrationProfileName
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

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


PROFILES: dict[MigrationProfileName, NistPqcMigrationProfile] = {
    "baseline": NistPqcMigrationProfile(
        name="baseline",
        description="Inventory and benchmark current classical cryptography before migration.",
        allowed_kems=[],
        allowed_signatures=[],
        allowed_classical_key_exchange=["rsa-2048", "rsa-3072", "ecdhe-p256", "x25519"],
        allowed_classical_signatures=["rsa-pkcs1-sha256", "rsa-pss-sha256", "ecdsa-p256-sha256", "ed25519"],
        preferred_key_exchange_order=["x25519", "ecdhe-p256", "rsa-3072", "rsa-2048"],
        min_rsa_bits=2048,
        allow_classical_only=True,
        require_hybrid=False,
        require_pqc=False,
        target_state="Establish a complete inventory, owners, and benchmark baseline.",
        retirement_guidance=["Mark RSA-2048 and ECC assets as migration candidates."],
    ),
    "hybrid_transition": NistPqcMigrationProfile(
        name="hybrid_transition",
        description="Deploy hybrid classical + PQC key establishment while preserving compatibility.",
        allowed_kems=["ml-kem-512", "ml-kem-768", "ml-kem-1024", "kyber768"],
        allowed_signatures=["ml-dsa-44", "ml-dsa-65", "slh-dsa-sha2-128s"],
        allowed_classical_key_exchange=["x25519", "ecdhe-p256", "ecdhe-p384", "rsa-3072"],
        allowed_classical_signatures=["rsa-pss-sha256", "rsa-pss-sha384", "ecdsa-p256-sha256", "ecdsa-p384-sha384"],
        preferred_key_exchange_order=["x25519+ml-kem-768", "ecdhe-p256+ml-kem-768", "x25519+kyber768"],
        min_rsa_bits=3072,
        allow_classical_only=False,
        require_hybrid=True,
        require_pqc=False,
        target_state="Hybrid mode for externally exposed and critical workloads.",
        retirement_guidance=["Stop introducing new RSA-2048 assets.", "Prefer ML-KEM-768 for general-purpose hybrid KEM trials."],
    ),
    "pqc_preferred": NistPqcMigrationProfile(
        name="pqc_preferred",
        description="Prefer standardized PQC algorithms, allowing hybrid fallback for interoperability.",
        allowed_kems=["ml-kem-768", "ml-kem-1024"],
        allowed_signatures=["ml-dsa-65", "ml-dsa-87", "slh-dsa-sha2-192s"],
        allowed_classical_key_exchange=["x25519", "ecdhe-p384"],
        allowed_classical_signatures=["ecdsa-p384-sha384", "rsa-pss-sha384"],
        preferred_key_exchange_order=["ml-kem-768", "ml-kem-1024", "x25519+ml-kem-768"],
        min_rsa_bits=3072,
        allow_classical_only=False,
        require_hybrid=False,
        require_pqc=True,
        target_state="PQC-first negotiation with hybrid fallback where required.",
        retirement_guidance=["Require exception records for classical-only services."],
    ),
    "strict_pqc": NistPqcMigrationProfile(
        name="strict_pqc",
        description="Permit only PQC key establishment and PQC signatures for controlled test zones.",
        allowed_kems=["ml-kem-768", "ml-kem-1024"],
        allowed_signatures=["ml-dsa-65", "ml-dsa-87"],
        allowed_classical_key_exchange=[],
        allowed_classical_signatures=[],
        preferred_key_exchange_order=["ml-kem-768", "ml-kem-1024"],
        min_rsa_bits=0,
        allow_classical_only=False,
        require_hybrid=False,
        require_pqc=True,
        target_state="PQC-only enclave or lab validation.",
        retirement_guidance=["Do not use in broad production until interoperability is proven."],
    ),
}


def list_profiles() -> list[NistPqcMigrationProfile]:
    return list(PROFILES.values())


def get_profile(name: str) -> NistPqcMigrationProfile:
    try:
        return PROFILES[name.lower()]  # type: ignore[index]
    except KeyError as exc:
        raise ValueError(f"Unknown migration profile: {name}") from exc
