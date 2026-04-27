from __future__ import annotations

from pydantic import BaseModel


class CryptoAssetResponse(BaseModel):
    environment: str
    asset_type: str
    name: str
    source: str
    algorithm: str
    key_size: int | None = None
    ready_to_migrate: bool
    exposure: str
    criticality: str
    owner: str | None = None
    service: str | None = None


class EnvironmentInventoryResponse(BaseModel):
    environment: str
    keys: int
    certificates: int
    ready_to_migrate: int
    assets: list[CryptoAssetResponse]


class InventoryScanResponse(BaseModel):
    scanned_at: str
    total_keys: int
    total_certificates: int
    total_ready_to_migrate: int
    environments: list[EnvironmentInventoryResponse]


class AssetReadinessResponse(BaseModel):
    environment: str
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


class EnvironmentReadinessResponse(BaseModel):
    environment: str
    asset_count: int
    average_risk_score: float
    average_readiness_score: float
    critical_assets: int
    high_risk_assets: int
    ready_to_migrate: int


class ReadinessReportResponse(BaseModel):
    scanned_at: str
    total_assets: int
    total_critical_assets: int
    total_high_risk_assets: int
    average_risk_score: float
    average_readiness_score: float
    environments: list[EnvironmentReadinessResponse]
    assets: list[AssetReadinessResponse]
