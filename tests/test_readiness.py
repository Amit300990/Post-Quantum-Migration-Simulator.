from __future__ import annotations

from app.core.inventory import CryptoAsset
from app.core.readiness import assess_asset, build_readiness_report


def test_public_critical_rsa_certificate_is_high_priority() -> None:
    asset = CryptoAsset(
        environment="aws",
        asset_type="certificate",
        name="api.example.com",
        source="aws:acm:us-east-1",
        algorithm="rsa-2048",
        key_size=2048,
        exposure="public",
        criticality="critical",
        owner="edge-platform",
    )

    assessment = assess_asset(asset)

    assert assessment.risk_level in {"critical", "high"}
    assert assessment.risk_score >= 80
    assert assessment.migration_priority.startswith("P0")


def test_readiness_report_contains_environment_summaries() -> None:
    report = build_readiness_report()

    assert report.total_assets > 0
    assert {env.environment for env in report.environments} == {"aws", "azure", "gcp", "on_prem"}


def test_unknown_unowned_asset_has_lower_readiness() -> None:
    asset = CryptoAsset(
        environment="on_prem",
        asset_type="key",
        name="mystery.key",
        source="/srv/mystery.key",
        algorithm="unknown",
        exposure="unknown",
        owner=None,
    )

    assessment = assess_asset(asset)

    assert assessment.readiness_score < 70
    assert "No owner recorded" in assessment.factors
    assert any("enrich inventory metadata" in action for action in assessment.recommended_actions)
