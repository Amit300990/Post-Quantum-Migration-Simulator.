from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Post-Quantum Migration Simulator"
    database_url: str = "sqlite:///./data/results.db"
    enabled_algorithms: list[str] = Field(default_factory=lambda: ["rsa", "kyber"])
    benchmark_file_sizes: list[int] = Field(default_factory=lambda: [1024, 1024 * 1024, 10 * 1024 * 1024])
    benchmark_iterations: int = 3
    output_dir: Path = Path("reports")
    kyber_algorithm: str = "Kyber768"
    rsa_key_size: int = 2048
    aes_key_size_bits: int = 256
    on_prem_scan_paths: list[Path] = Field(default_factory=lambda: [Path("data/on_prem")])
    aws_inventory_file: Path = Path("data/aws_inventory.json")
    azure_inventory_file: Path = Path("data/azure_inventory.json")
    gcp_inventory_file: Path = Path("data/gcp_inventory.json")
    max_scan_file_bytes: int = 2 * 1024 * 1024

    model_config = SettingsConfigDict(
        env_prefix="PQMS_",
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
