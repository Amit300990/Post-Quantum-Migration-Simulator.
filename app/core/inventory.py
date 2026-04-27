from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Literal

from app.utils.config import get_settings


EnvironmentName = Literal["aws", "azure", "gcp", "on_prem"]
AssetType = Literal["key", "certificate"]

KEY_EXTENSIONS = {".key", ".pem", ".p8", ".p12", ".pfx", ".jks", ".keystore"}
CERT_EXTENSIONS = {".crt", ".cer", ".cert", ".pem", ".p7b", ".p7c"}
KEY_MARKERS = (
    "BEGIN PRIVATE KEY",
    "BEGIN RSA PRIVATE KEY",
    "BEGIN EC PRIVATE KEY",
    "BEGIN PUBLIC KEY",
    "BEGIN RSA PUBLIC KEY",
)
CERT_MARKERS = ("BEGIN CERTIFICATE", "BEGIN X509 CERTIFICATE")
CLASSICAL_ALGORITHMS = {"rsa", "rsa-2048", "rsa-3072", "rsa-4096", "ecc", "ec", "ecdsa", "ed25519", "x25519"}


@dataclass(frozen=True)
class CryptoAsset:
    environment: EnvironmentName
    asset_type: AssetType
    name: str
    source: str
    algorithm: str = "unknown"
    key_size: int | None = None
    ready_to_migrate: bool = True
    exposure: str = "unknown"
    criticality: str = "medium"
    owner: str | None = None
    service: str | None = None


@dataclass(frozen=True)
class EnvironmentInventory:
    environment: EnvironmentName
    keys: int
    certificates: int
    ready_to_migrate: int
    assets: list[CryptoAsset] = field(default_factory=list)


@dataclass(frozen=True)
class InventoryScanReport:
    scanned_at: str
    total_keys: int
    total_certificates: int
    total_ready_to_migrate: int
    environments: list[EnvironmentInventory]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _infer_algorithm(text: str, name: str) -> str:
    searchable = f"{name}\n{text}".lower()
    if "rsa" in searchable:
        return "rsa"
    if "ecdsa" in searchable or "ec private key" in searchable or "ecc" in searchable:
        return "ecc"
    if "kyber" in searchable or "ml-kem" in searchable:
        return "pqc"
    return "unknown"


def _is_ready_to_migrate(algorithm: str) -> bool:
    normalized = algorithm.lower()
    return normalized in CLASSICAL_ALGORITHMS or normalized == "unknown"


def _asset_from_record(environment: EnvironmentName, record: dict[str, object]) -> CryptoAsset | None:
    raw_type = str(record.get("asset_type", record.get("type", ""))).lower()
    if raw_type not in {"key", "certificate", "cert"}:
        return None
    asset_type: AssetType = "certificate" if raw_type in {"certificate", "cert"} else "key"
    algorithm = str(record.get("algorithm", "unknown")).lower()
    return CryptoAsset(
        environment=environment,
        asset_type=asset_type,
        name=str(record.get("name", record.get("id", "unnamed-asset"))),
        source=str(record.get("source", environment)),
        algorithm=algorithm,
        key_size=int(record["key_size"]) if record.get("key_size") is not None else None,
        ready_to_migrate=bool(record.get("ready_to_migrate", _is_ready_to_migrate(algorithm))),
        exposure=str(record.get("exposure", "unknown")).lower(),
        criticality=str(record.get("criticality", "medium")).lower(),
        owner=str(record["owner"]) if record.get("owner") is not None else None,
        service=str(record["service"]) if record.get("service") is not None else None,
    )


class CloudInventoryScanner:
    def __init__(self, environment: EnvironmentName, inventory_file: Path) -> None:
        self.environment = environment
        self.inventory_file = inventory_file

    def scan(self) -> list[CryptoAsset]:
        if not self.inventory_file.exists():
            return []
        records = json.loads(self.inventory_file.read_text(encoding="utf-8"))
        if not isinstance(records, list):
            raise ValueError(f"Inventory file must contain a JSON list: {self.inventory_file}")
        return [
            asset
            for record in records
            if isinstance(record, dict)
            for asset in [_asset_from_record(self.environment, record)]
            if asset is not None
        ]


class OnPremInventoryScanner:
    def __init__(self, roots: Iterable[Path], max_file_bytes: int) -> None:
        self.roots = list(roots)
        self.max_file_bytes = max_file_bytes

    def scan(self) -> list[CryptoAsset]:
        assets: list[CryptoAsset] = []
        for root in self.roots:
            if not root.exists():
                continue
            files = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
            for path in files:
                assets.extend(self._scan_file(path))
        return assets

    def _scan_file(self, path: Path) -> list[CryptoAsset]:
        suffix = path.suffix.lower()
        if suffix not in KEY_EXTENSIONS | CERT_EXTENSIONS:
            return []
        if path.stat().st_size > self.max_file_bytes:
            return []

        try:
            raw = path.read_bytes()
            text = raw.decode("utf-8", errors="ignore")
        except OSError:
            return []

        assets: list[CryptoAsset] = []
        has_key = suffix in KEY_EXTENSIONS or any(marker in text for marker in KEY_MARKERS)
        has_cert = suffix in CERT_EXTENSIONS or any(marker in text for marker in CERT_MARKERS)
        algorithm = _infer_algorithm(text, path.name)
        source = str(path)

        if has_key:
            assets.append(
                CryptoAsset(
                    environment="on_prem",
                    asset_type="key",
                    name=path.name,
                    source=source,
                    algorithm=algorithm,
                    ready_to_migrate=_is_ready_to_migrate(algorithm),
                    exposure="internal",
                    criticality="medium",
                )
            )
        if has_cert:
            assets.append(
                CryptoAsset(
                    environment="on_prem",
                    asset_type="certificate",
                    name=path.name,
                    source=source,
                    algorithm=algorithm,
                    ready_to_migrate=_is_ready_to_migrate(algorithm),
                    exposure="internal",
                    criticality="medium",
                )
            )
        return assets


def summarize_environment(environment: EnvironmentName, assets: list[CryptoAsset]) -> EnvironmentInventory:
    return EnvironmentInventory(
        environment=environment,
        keys=sum(asset.asset_type == "key" for asset in assets),
        certificates=sum(asset.asset_type == "certificate" for asset in assets),
        ready_to_migrate=sum(asset.ready_to_migrate for asset in assets),
        assets=assets,
    )


def scan_all_environments() -> InventoryScanReport:
    settings = get_settings()
    scanners: dict[EnvironmentName, object] = {
        "aws": CloudInventoryScanner("aws", settings.aws_inventory_file),
        "azure": CloudInventoryScanner("azure", settings.azure_inventory_file),
        "gcp": CloudInventoryScanner("gcp", settings.gcp_inventory_file),
        "on_prem": OnPremInventoryScanner(settings.on_prem_scan_paths, settings.max_scan_file_bytes),
    }

    inventories: list[EnvironmentInventory] = []
    for environment, scanner in scanners.items():
        assets = scanner.scan()  # type: ignore[attr-defined]
        inventories.append(summarize_environment(environment, assets))

    return InventoryScanReport(
        scanned_at=_now(),
        total_keys=sum(inventory.keys for inventory in inventories),
        total_certificates=sum(inventory.certificates for inventory in inventories),
        total_ready_to_migrate=sum(inventory.ready_to_migrate for inventory in inventories),
        environments=inventories,
    )
