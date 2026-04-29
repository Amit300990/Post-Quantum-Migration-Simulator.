from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values
from pydantic import BaseModel, Field

ROOT_DIR = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT_DIR / "config.yaml"
ENV_PATH = ROOT_DIR / ".env"


def load_yaml_config() -> dict[str, Any]:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as stream:
            return yaml.safe_load(stream) or {}
    logging.getLogger("pqms").warning("config.yaml not found at %s; using defaults", CONFIG_PATH)
    return {}


def load_env_config() -> dict[str, Any]:
    env_values = dotenv_values(ENV_PATH)
    parsed: dict[str, Any] = {}

    if env_values.get("ALGORITHMS_ENABLED"):
        parsed["algorithms_enabled"] = [
            item.strip() for item in env_values["ALGORITHMS_ENABLED"].split(",") if item.strip()
        ]
    if env_values.get("BENCHMARK_SIZES"):
        parsed["benchmark_sizes"] = [
            int(item.strip()) for item in env_values["BENCHMARK_SIZES"].split(",") if item.strip()
        ]
    if env_values.get("DATABASE_URL"):
        parsed["database_url"] = env_values["DATABASE_URL"]
    if env_values.get("OUTPUT_PATH"):
        parsed["output_path"] = env_values["OUTPUT_PATH"]
    if env_values.get("KYBER_MODE"):
        parsed["kyber_mode"] = env_values["KYBER_MODE"]
    if env_values.get("RSA_KEY_SIZE"):
        parsed["rsa_key_size"] = int(env_values["RSA_KEY_SIZE"])
    if env_values.get("BENCHMARK_ITERATIONS"):
        parsed["benchmark_iterations"] = int(env_values["BENCHMARK_ITERATIONS"])
    if env_values.get("AWS_INVENTORY_FILE"):
        parsed["aws_inventory_file"] = Path(env_values["AWS_INVENTORY_FILE"])
    if env_values.get("AZURE_INVENTORY_FILE"):
        parsed["azure_inventory_file"] = Path(env_values["AZURE_INVENTORY_FILE"])
    if env_values.get("GCP_INVENTORY_FILE"):
        parsed["gcp_inventory_file"] = Path(env_values["GCP_INVENTORY_FILE"])
    if env_values.get("ON_PREM_SCAN_PATHS"):
        parsed["on_prem_scan_paths"] = [
            Path(p.strip()) for p in env_values["ON_PREM_SCAN_PATHS"].split(",") if p.strip()
        ]
    if env_values.get("MAX_SCAN_FILE_BYTES"):
        parsed["max_scan_file_bytes"] = int(env_values["MAX_SCAN_FILE_BYTES"])

    return parsed


class Settings(BaseModel):
    database_url: str = Field("sqlite:///./data/results.db")
    algorithms_enabled: list[str] = Field(["rsa", "kyber"])
    benchmark_iterations: int = Field(3)
    benchmark_sizes: list[int] = Field([1024, 1048576, 10485760])
    output_path: str = Field("./reports")
    kyber_mode: str = Field("Kyber512")
    rsa_key_size: int = Field(2048)
    aws_inventory_file: Path = Field(default_factory=lambda: ROOT_DIR / "data" / "aws_inventory.json")
    azure_inventory_file: Path = Field(default_factory=lambda: ROOT_DIR / "data" / "azure_inventory.json")
    gcp_inventory_file: Path = Field(default_factory=lambda: ROOT_DIR / "data" / "gcp_inventory.json")
    on_prem_scan_paths: list[Path] = Field(default_factory=lambda: [ROOT_DIR / "data" / "on_prem"])
    max_scan_file_bytes: int = Field(1_048_576)


yaml_values = load_yaml_config()
env_values = load_env_config()
settings = Settings(**{**yaml_values, **env_values})


def get_settings() -> Settings:
    return settings
