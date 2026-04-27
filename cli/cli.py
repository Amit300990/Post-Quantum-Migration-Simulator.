from __future__ import annotations

import json

import typer

from app.core.hsm import get_hsm_client
from app.core.inventory import scan_all_environments
from app.core.negotiation import NegotiationParty, negotiate_algorithms
from app.core.profiles import list_profiles
from app.core.readiness import build_readiness_report


app = typer.Typer(help="Post-Quantum Migration Simulator CLI")


@app.command()
def inventory() -> None:
    """Scan AWS, Azure, GCP, and on-prem crypto inventory."""
    report = scan_all_environments()
    typer.echo(json.dumps(report.to_dict(), indent=2))


@app.command()
def readiness() -> None:
    """Score discovered crypto assets and generate a PQC migration readiness report."""
    report = build_readiness_report()
    typer.echo(json.dumps(report.to_dict(), indent=2))


@app.command("profiles")
def profiles() -> None:
    """List NIST-style PQC migration profiles."""
    typer.echo(json.dumps([profile.to_dict() for profile in list_profiles()], indent=2))


@app.command("negotiate")
def negotiate(
    profile: str = "hybrid_transition",
    client_kex: str = "x25519+ml-kem-768,x25519,rsa-2048",
    server_kex: str = "x25519+ml-kem-768,ecdhe-p256,rsa-3072",
    client_sig: str = "ecdsa-p256-sha256,ml-dsa-65",
    server_sig: str = "ecdsa-p256-sha256,ml-dsa-65",
) -> None:
    """Run TLS-style algorithm negotiation under a migration profile."""
    result = negotiate_algorithms(
        client=NegotiationParty(client_kex.split(","), client_sig.split(",")),
        server=NegotiationParty(server_kex.split(","), server_sig.split(",")),
        profile_name=profile,
    )
    typer.echo(json.dumps(result.to_dict(), indent=2))


@app.command("hsm-sim")
def hsm_sim(
    label: str = "migration-wrapping-key",
    algorithm: str = "ml-kem-768",
    key_size: int = 256,
) -> None:
    """Generate a key in the software HSM simulator."""
    client = get_hsm_client("software")
    key = client.generate_key(label=label, algorithm=algorithm, key_size=key_size)
    typer.echo(json.dumps(key.__dict__, indent=2))


if __name__ == "__main__":
    app()
