from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import fmean

from app.core.inventory import CLASSICAL_ALGORITHMS, CryptoAsset, EnvironmentName, InventoryScanReport, scan_all_environments


RISK_LEVELS = (
    (80, "critical"),
    (60, "high"),
    (35, "medium"),
    (0, "low"),
)


@dataclass(frozen=True)
class AssetReadinessAssessment:
    environment: EnvironmentName
    asset_name: str
    asset_type: str
    source: str
    algorithm: str
    risk_score: int
    readiness_score: int
    risk_level: str
    migration_priority: str
    factors: list[str]
    recommended_actions: list[str]


@dataclass(frozen=True)
class EnvironmentReadinessSummary:
    environment: EnvironmentName
    asset_count: int
    average_risk_score: float
    average_readiness_score: float
    critical_assets: int
    high_risk_assets: int
    ready_to_migrate: int


@dataclass(frozen=True)
class ReadinessReport:
    scanned_at: str
    total_assets: int
    total_critical_assets: int
    total_high_risk_assets: int
    average_risk_score: float
    average_readiness_score: float
    environments: list[EnvironmentReadinessSummary]
    assets: list[AssetReadinessAssessment]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _risk_level(score: int) -> str:
    for minimum, level in RISK_LEVELS:
        if score >= minimum:
            return level
    return "low"


def _priority(level: str) -> str:
    return {
        "critical": "P0 - migrate first",
        "high": "P1 - plan this wave",
        "medium": "P2 - schedule after high-risk assets",
        "low": "P3 - monitor or defer",
    }[level]


def _is_classical(algorithm: str) -> bool:
    normalized = algorithm.lower()
    return normalized in CLASSICAL_ALGORITHMS or normalized in {"rsa", "ecc", "ecdsa", "ec"}


def assess_asset(asset: CryptoAsset) -> AssetReadinessAssessment:
    score = 0
    factors: list[str] = []
    actions: list[str] = []
    algorithm = asset.algorithm.lower()

    if _is_classical(algorithm):
        score += 35
        factors.append("Uses quantum-vulnerable classical cryptography")
        actions.append("Plan replacement with hybrid classical + PQC mode before PQC-only migration")
    elif algorithm == "unknown":
        score += 25
        factors.append("Algorithm could not be identified")
        actions.append("Inspect the asset and enrich inventory metadata before migration planning")
    elif algorithm in {"pqc", "kyber", "ml-kem"}:
        factors.append("Already uses a post-quantum or PQC-labeled algorithm")
        actions.append("Validate interoperability and benchmark operational performance")

    if asset.asset_type == "key":
        score += 15
        factors.append("Private or managed key material requires controlled rotation")
        actions.append("Create a rotation plan with rollback and dual-key support")
    else:
        score += 10
        factors.append("Certificate migration can increase handshake payload size")
        actions.append("Model certificate-chain size and TLS handshake impact")

    if algorithm.startswith("rsa") and asset.key_size is not None and asset.key_size < 3072:
        score += 10
        factors.append("RSA key size is below 3072-bit transition guidance")
        actions.append("Prioritize hybrid migration over simply increasing RSA key size")

    exposure = asset.exposure.lower()
    if exposure in {"public", "internet", "external"}:
        score += 20
        factors.append("Asset is externally exposed")
        actions.append("Pilot hybrid TLS/KEM mode in a controlled public-facing service")
    elif exposure in {"internal", "private"}:
        score += 6
        factors.append("Asset is internally exposed")
    else:
        score += 8
        factors.append("Exposure is unknown")
        actions.append("Classify network exposure and consuming applications")

    criticality = asset.criticality.lower()
    if criticality == "critical":
        score += 20
        factors.append("Supports a critical workload")
        actions.append("Assign an owner and migration window before production changes")
    elif criticality == "high":
        score += 12
        factors.append("Supports a high-criticality workload")
    elif criticality == "low":
        score += 2
    else:
        score += 6

    if asset.owner is None:
        score += 5
        factors.append("No owner recorded")
        actions.append("Assign accountable service owner")

    if "prod" in asset.source.lower() or "prod" in asset.name.lower():
        score += 8
        factors.append("Appears to be production-related")

    risk_score = min(score, 100)
    readiness_penalty = 0
    if algorithm == "unknown":
        readiness_penalty += 25
    if asset.owner is None:
        readiness_penalty += 10
    if exposure == "unknown":
        readiness_penalty += 10
    if not asset.ready_to_migrate:
        readiness_penalty += 40
    if criticality in {"critical", "high"}:
        readiness_penalty += 5

    readiness_score = max(0, min(100, 100 - readiness_penalty))
    level = _risk_level(risk_score)
    deduped_actions = list(dict.fromkeys(actions))

    return AssetReadinessAssessment(
        environment=asset.environment,
        asset_name=asset.name,
        asset_type=asset.asset_type,
        source=asset.source,
        algorithm=asset.algorithm,
        risk_score=risk_score,
        readiness_score=readiness_score,
        risk_level=level,
        migration_priority=_priority(level),
        factors=factors,
        recommended_actions=deduped_actions,
    )


def build_readiness_report(scan_report: InventoryScanReport | None = None) -> ReadinessReport:
    report = scan_report or scan_all_environments()
    assessments = [assess_asset(asset) for inventory in report.environments for asset in inventory.assets]
    environment_summaries: list[EnvironmentReadinessSummary] = []

    for inventory in report.environments:
        env_assessments = [asset for asset in assessments if asset.environment == inventory.environment]
        environment_summaries.append(
            EnvironmentReadinessSummary(
                environment=inventory.environment,
                asset_count=len(env_assessments),
                average_risk_score=round(fmean(asset.risk_score for asset in env_assessments), 2)
                if env_assessments
                else 0.0,
                average_readiness_score=round(fmean(asset.readiness_score for asset in env_assessments), 2)
                if env_assessments
                else 0.0,
                critical_assets=sum(asset.risk_level == "critical" for asset in env_assessments),
                high_risk_assets=sum(asset.risk_level == "high" for asset in env_assessments),
                ready_to_migrate=inventory.ready_to_migrate,
            )
        )

    return ReadinessReport(
        scanned_at=report.scanned_at,
        total_assets=len(assessments),
        total_critical_assets=sum(asset.risk_level == "critical" for asset in assessments),
        total_high_risk_assets=sum(asset.risk_level == "high" for asset in assessments),
        average_risk_score=round(fmean(asset.risk_score for asset in assessments), 2) if assessments else 0.0,
        average_readiness_score=round(fmean(asset.readiness_score for asset in assessments), 2) if assessments else 0.0,
        environments=environment_summaries,
        assets=assessments,
    )
