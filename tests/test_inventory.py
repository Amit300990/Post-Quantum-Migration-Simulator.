from __future__ import annotations

from pathlib import Path

import pytest

from app.core.inventory import CloudInventoryScanner, OnPremInventoryScanner, scan_all_environments


def test_on_prem_scanner_finds_keys_and_certificates(tmp_path: Path) -> None:
    pem = tmp_path / "service.pem"
    pem.write_text(
        "-----BEGIN CERTIFICATE-----\nabc\n-----END CERTIFICATE-----\n"
        "-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n",
        encoding="utf-8",
    )

    assets = OnPremInventoryScanner([tmp_path], max_file_bytes=4096).scan()

    assert sum(asset.asset_type == "key" for asset in assets) == 1
    assert sum(asset.asset_type == "certificate" for asset in assets) == 1
    assert all(asset.ready_to_migrate for asset in assets)


def test_full_inventory_report_has_all_environments() -> None:
    report = scan_all_environments()

    assert {inventory.environment for inventory in report.environments} == {"aws", "azure", "gcp", "on_prem"}


def test_on_prem_scanner_ignores_files_above_size_limit(tmp_path: Path) -> None:
    oversized = tmp_path / "large.pem"
    oversized.write_text("-----BEGIN RSA PRIVATE KEY-----\nabc\n-----END RSA PRIVATE KEY-----\n", encoding="utf-8")

    assets = OnPremInventoryScanner([tmp_path], max_file_bytes=1).scan()

    assert assets == []


def test_on_prem_scanner_handles_missing_path(tmp_path: Path) -> None:
    assets = OnPremInventoryScanner([tmp_path / "missing"], max_file_bytes=4096).scan()

    assert assets == []


def test_cloud_inventory_scanner_rejects_non_list_json(tmp_path: Path) -> None:
    inventory_file = tmp_path / "inventory.json"
    inventory_file.write_text('{"asset_type": "key"}', encoding="utf-8")

    scanner = CloudInventoryScanner("aws", inventory_file)

    with pytest.raises(ValueError, match="JSON list"):
        scanner.scan()


def test_cloud_inventory_scanner_ignores_unknown_asset_types(tmp_path: Path) -> None:
    inventory_file = tmp_path / "inventory.json"
    inventory_file.write_text('[{"asset_type": "secret", "name": "ignored"}]', encoding="utf-8")

    scanner = CloudInventoryScanner("gcp", inventory_file)

    assert scanner.scan() == []
