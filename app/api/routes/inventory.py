from __future__ import annotations

from fastapi import APIRouter

from app.core.inventory import scan_all_environments
from app.core.readiness import build_readiness_report
from app.schemas.inventory import InventoryScanResponse, ReadinessReportResponse


router = APIRouter(tags=["inventory"])


@router.post("/inventory/scan", response_model=InventoryScanResponse)
def scan_inventory() -> dict[str, object]:
    return scan_all_environments().to_dict()


@router.get("/inventory/environments", response_model=InventoryScanResponse)
def get_environment_inventory() -> dict[str, object]:
    return scan_all_environments().to_dict()


@router.get("/readiness", response_model=ReadinessReportResponse)
def get_readiness_report() -> dict[str, object]:
    return build_readiness_report().to_dict()
