from __future__ import annotations

from app.core.hsm import get_hsm_client
from app.core.negotiation import NegotiationParty, negotiate_algorithms
from app.core.profiles import get_profile, list_profiles

import pytest


def test_profiles_include_hybrid_transition() -> None:
    profiles = {profile.name for profile in list_profiles()}

    assert "hybrid_transition" in profiles
    assert get_profile("hybrid_transition").require_hybrid is True


def test_negotiation_prefers_hybrid_for_transition_profile() -> None:
    result = negotiate_algorithms(
        client=NegotiationParty(
            key_exchange_algorithms=["x25519", "x25519+ml-kem-768"],
            signature_algorithms=["ecdsa-p256-sha256", "ml-dsa-65"],
        ),
        server=NegotiationParty(
            key_exchange_algorithms=["x25519+ml-kem-768", "rsa-3072"],
            signature_algorithms=["ecdsa-p256-sha256"],
        ),
        profile_name="hybrid_transition",
    )

    assert result.status == "negotiated"
    assert result.protocol_mode == "hybrid"
    assert result.selected_key_exchange == "x25519+ml-kem-768"


def test_negotiation_fails_when_profile_requires_hybrid() -> None:
    result = negotiate_algorithms(
        client=NegotiationParty(
            key_exchange_algorithms=["x25519"],
            signature_algorithms=["ecdsa-p256-sha256"],
        ),
        server=NegotiationParty(
            key_exchange_algorithms=["x25519"],
            signature_algorithms=["ecdsa-p256-sha256"],
        ),
        profile_name="hybrid_transition",
    )

    assert result.status == "failed"
    assert result.failure_reason == "Profile requires hybrid key exchange."


def test_software_hsm_generates_and_wraps_key() -> None:
    client = get_hsm_client("software")
    key = client.generate_key("test-key", "ml-kem-768", 256)
    result = client.wrap_key(key.key_id, b"0123456789abcdef0123456789abcdef")

    assert key.exportable is False
    assert result.operation == "wrap_key"
    assert result.result_size == 32


def test_profile_lookup_rejects_unknown_profile() -> None:
    with pytest.raises(ValueError, match="Unknown migration profile"):
        get_profile("made_up_profile")


def test_negotiation_fails_when_signature_has_no_common_profile_match() -> None:
    result = negotiate_algorithms(
        client=NegotiationParty(
            key_exchange_algorithms=["x25519+ml-kem-768"],
            signature_algorithms=["ed25519"],
        ),
        server=NegotiationParty(
            key_exchange_algorithms=["x25519+ml-kem-768"],
            signature_algorithms=["ed25519"],
        ),
        profile_name="hybrid_transition",
    )

    assert result.status == "failed"
    assert result.failure_reason == "No mutually supported signature algorithm is allowed by the selected profile."


def test_hsm_wrap_rejects_unknown_key_id() -> None:
    client = get_hsm_client("software")

    with pytest.raises(KeyError, match="Unknown HSM key id"):
        client.wrap_key("does-not-exist", b"key material")


def test_hsm_factory_rejects_unknown_provider() -> None:
    with pytest.raises(ValueError, match="Unsupported HSM provider"):
        get_hsm_client("hardware-that-is-not-configured")
