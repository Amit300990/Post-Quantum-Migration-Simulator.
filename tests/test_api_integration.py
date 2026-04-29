from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_profiles_endpoint_returns_known_profiles() -> None:
    response = client.get("/profiles")

    assert response.status_code == 200
    names = {profile["name"] for profile in response.json()}
    assert {"baseline", "hybrid_transition", "pqc_preferred", "strict_pqc"}.issubset(names)


def test_negotiation_endpoint_success() -> None:
    response = client.post(
        "/negotiate",
        json={
            "profile": "hybrid_transition",
            "client": {
                "key_exchange_algorithms": ["x25519+ml-kem-768", "x25519"],
                "signature_algorithms": ["ecdsa-p256-sha256"],
            },
            "server": {
                "key_exchange_algorithms": ["x25519+ml-kem-768"],
                "signature_algorithms": ["ecdsa-p256-sha256"],
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "negotiated"
    assert body["protocol_mode"] == "hybrid"


def test_inventory_endpoint_returns_all_environments() -> None:
    response = client.get("/inventory/environments")

    assert response.status_code == 200
    environments = {item["environment"] for item in response.json()["environments"]}
    assert environments == {"aws", "azure", "gcp", "on_prem"}
