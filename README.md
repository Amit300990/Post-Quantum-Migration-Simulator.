# Post-Quantum Migration Simulator

An end-to-end Python platform for simulating migration from classical cryptography to post-quantum cryptography.

The simulator combines crypto workflows, benchmark analysis, cloud/on-prem crypto inventory discovery, PQC readiness scoring, NIST-style migration profiles, TLS-style algorithm negotiation, HSM simulation, FastAPI endpoints, a Streamlit dashboard, Typer CLI commands, and pytest coverage.

## Capabilities

- RSA-2048 + AES-256-GCM hybrid encryption support.
- Kyber/ML-KEM-style KEM integration through `liboqs-python`.
- Classical and PQC handshake simulation.
- Benchmarking for key generation, encryption, decryption, ciphertext size, key size, and throughput.
- AWS, Azure, GCP, and on-prem crypto inventory scanning.
- PQC migration risk and readiness scoring.
- NIST-style migration profiles.
- TLS-style algorithm negotiation.
- Software HSM simulator abstraction.
- API, CLI, dashboard, and tests.

## Architecture

```text
                       +----------------------+
                       |      User / CLI      |
                       +----------+-----------+
                                  |
                                  v
+-------------+          +--------+---------+          +----------------+
| Streamlit   | <------> | FastAPI Backend  | <------> | Core Services  |
| Dashboard   |          | app/main.py      |          | app/core       |
+-------------+          +--------+---------+          +-------+--------+
                                  |
                                  v
                         +--------+---------+
                         | SQLite / Reports |
                         | data/, reports/  |
                         +------------------+
```

Core modules:

```text
app/core/classical/     RSA and AES-GCM primitives
app/core/pqc/           Kyber/liboqs wrapper and KDF
app/core/hybrid.py      RSA/Kyber hybrid encryption facades
app/core/handshake.py   Classical and PQC handshake simulation
app/core/benchmark.py   Benchmark engine
app/core/inventory.py   AWS/Azure/GCP/on-prem crypto inventory scanner
app/core/readiness.py   PQC risk and readiness scoring
app/core/profiles.py    NIST-style PQC migration profiles
app/core/negotiation.py TLS-style algorithm negotiation
app/core/hsm.py         Software HSM simulator abstraction
```

## Project Structure

```text
post-quantum-migration-simulator/
  app/
    main.py
    api/routes/
      benchmark.py
      crypto.py
      handshake.py
      inventory.py
      migration.py
      results.py
    core/
      classical/
        aes.py
        rsa.py
      pqc/
        kyber.py
      benchmark.py
      handshake.py
      hsm.py
      hybrid.py
      inventory.py
      negotiation.py
      profiles.py
      readiness.py
    db/
    schemas/
    utils/

  cli/
    cli.py
  dashboard/
    app.py
  data/
  reports/
  tests/
  requirements.txt
  Dockerfile
  docker-compose.yml
  README.md
```

## Requirements

- Python 3.11+
- `cryptography`
- `FastAPI`
- `SQLAlchemy`
- `Streamlit`
- `Pandas`
- `Plotly`
- `Typer`
- `pytest`
- Optional for real PQC KEM execution: native `liboqs` and `liboqs-python`

Kyber support depends on Open Quantum Safe native libraries. If `liboqs-python` or native `liboqs` is unavailable, Kyber operations are environment-dependent. RSA/AES, inventory, readiness, negotiation, HSM simulation, CLI, dashboard, and most tests do not require liboqs.

## Setup

```bash
cd post-quantum-migration-simulator
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `liboqs-python` cannot install in your environment, install the remaining dependencies and use the classical, inventory, readiness, negotiation, HSM, API, CLI, and dashboard features while configuring liboqs separately.

## Configuration

Configuration is handled through environment variables with the `PQMS_` prefix.

Common settings:

```bash
export PQMS_DATABASE_URL="sqlite:///./data/results.db"
export PQMS_KYBER_ALGORITHM="Kyber768"
export PQMS_RSA_KEY_SIZE="2048"
export PQMS_BENCHMARK_ITERATIONS="3"
export PQMS_AWS_INVENTORY_FILE="data/aws_inventory.json"
export PQMS_AZURE_INVENTORY_FILE="data/azure_inventory.json"
export PQMS_GCP_INVENTORY_FILE="data/gcp_inventory.json"
```

Default on-prem scan path:

```text
data/on_prem
```

## Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Health check:

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

## API Endpoints

Implemented endpoints:

```text
GET  /health

POST /inventory/scan
GET  /inventory/environments
GET  /readiness

GET  /profiles
POST /negotiate

POST /hsm/keys
POST /hsm/wrap
```

Scaffolded endpoint groups:

```text
GET    /algorithms
POST   /encrypt
POST   /decrypt
POST   /benchmark
POST   /handshake
GET    /results
GET    /export
```

## CLI Usage

Run commands from the project root:

```bash
python cli/cli.py --help
```

### Inventory Scan

```bash
python cli/cli.py inventory
```

The inventory scan reads:

- `data/aws_inventory.json`
- `data/azure_inventory.json`
- `data/gcp_inventory.json`
- `data/on_prem`

Sample output shape:

```json
{
  "scanned_at": "2026-04-27T00:00:00+00:00",
  "total_keys": 4,
  "total_certificates": 4,
  "total_ready_to_migrate": 8,
  "environments": []
}
```

### PQC Readiness

```bash
python cli/cli.py readiness
```

The readiness engine scores assets by:

- algorithm family
- key size
- key or certificate type
- public/internal/unknown exposure
- workload criticality
- owner metadata
- production indicators

Output includes:

- `risk_score`
- `readiness_score`
- `risk_level`
- `migration_priority`
- `factors`
- `recommended_actions`

### NIST-Style Migration Profiles

```bash
python cli/cli.py profiles
```

Available profiles:

- `baseline`: inventory and benchmark current classical crypto
- `hybrid_transition`: require hybrid classical + PQC negotiation
- `pqc_preferred`: prefer standardized PQC with hybrid fallback
- `strict_pqc`: PQC-only lab or enclave testing

### TLS-Style Algorithm Negotiation

```bash
python cli/cli.py negotiate \
  --profile hybrid_transition \
  --client-kex x25519+ml-kem-768,x25519,rsa-2048 \
  --server-kex x25519+ml-kem-768,ecdhe-p256,rsa-3072 \
  --client-sig ecdsa-p256-sha256,ml-dsa-65 \
  --server-sig ecdsa-p256-sha256,ml-dsa-65
```

Example result:

```json
{
  "status": "negotiated",
  "profile": "hybrid_transition",
  "selected_key_exchange": "x25519+ml-kem-768",
  "selected_signature": "ecdsa-p256-sha256",
  "protocol_mode": "hybrid",
  "failure_reason": null
}
```

### Software HSM Simulator

```bash
python cli/cli.py hsm-sim \
  --label migration-wrapping-key \
  --algorithm ml-kem-768 \
  --key-size 256
```

The HSM module is currently a software simulator with an abstraction suitable for later providers:

- PKCS#11
- AWS CloudHSM
- Azure Managed HSM
- GCP Cloud HSM
- vendor appliances

## Dashboard

Run the Streamlit dashboard:

```bash
streamlit run dashboard/app.py
```

Dashboard tabs:

- Overview
- RSA vs PQC comparison
- Handshake comparison
- Crypto inventory
- Readiness

The `Crypto inventory` tab shows per-environment counts for:

- crypto keys
- certificates
- assets ready to migrate

The `Readiness` tab shows:

- total asset count
- average risk
- average readiness
- critical assets
- environment-level risk/readiness chart
- prioritized migration backlog

## Crypto Inventory Inputs

Cloud inventory files are JSON arrays. Example:

```json
[
  {
    "asset_type": "certificate",
    "name": "api.example.com",
    "source": "aws:acm:us-east-1",
    "algorithm": "rsa-2048",
    "key_size": 2048,
    "exposure": "public",
    "criticality": "critical",
    "owner": "edge-platform",
    "service": "public-api"
  }
]
```

Supported `asset_type` values:

- `key`
- `certificate`
- `cert`

Useful metadata:

- `algorithm`
- `key_size`
- `exposure`: `public`, `internal`, `private`, `unknown`
- `criticality`: `critical`, `high`, `medium`, `low`
- `owner`
- `service`

On-prem scanning detects common file types:

```text
.key
.pem
.p8
.p12
.pfx
.jks
.keystore
.crt
.cer
.cert
.p7b
.p7c
```

It also detects PEM markers such as:

```text
BEGIN PRIVATE KEY
BEGIN RSA PRIVATE KEY
BEGIN EC PRIVATE KEY
BEGIN PUBLIC KEY
BEGIN CERTIFICATE
```

## Crypto Workflows

### RSA Hybrid Encryption

The RSA hybrid provider:

1. Generates a random AES-256 key.
2. Encrypts data with AES-256-GCM.
3. Wraps the AES key with RSA-OAEP.
4. Returns ciphertext, nonce, tag, wrapped key, and metadata.

Metadata includes:

- `algorithm`
- `key_size`
- `timestamp`
- `mode`

### Kyber / PQC Hybrid Encryption

The Kyber provider:

1. Generates or loads a Kyber KEM key pair.
2. Encapsulates a shared secret.
3. Derives an AES-256 key through HKDF-SHA256.
4. Encrypts data with AES-256-GCM.
5. Stores the KEM ciphertext needed for decapsulation.

This requires `liboqs-python` and native OQS support.

## Testing

Run all tests:

```bash
python -m pytest tests
```

Run focused tests:

```bash
python -m pytest tests/test_crypto.py
python -m pytest tests/test_inventory.py
python -m pytest tests/test_readiness.py
python -m pytest tests/test_migration_profiles.py
python -m pytest tests/test_api_integration.py
```

The suite covers:

- AES-GCM correctness and tamper detection
- RSA hybrid encryption/decryption
- serialization round trips
- unsupported algorithm failures
- benchmark metrics and edge cases
- inventory scanner edge cases
- readiness scoring
- NIST profile lookup
- TLS-style negotiation success/failure paths
- HSM simulator success/failure paths
- FastAPI integration endpoints

Some tests use `pytest.importorskip` so they skip cleanly when optional dependencies such as `cryptography`, `fastapi`, `httpx`, or native `liboqs` bindings are not installed.

## Docker

Build and run:

```bash
docker-compose up --build
```

Expected services:

- backend FastAPI service
- Streamlit dashboard service

Typical URLs:

```text
Backend:   http://localhost:8000
Dashboard: http://localhost:8501
```

Note: real Kyber execution inside Docker requires the image to include native `liboqs` libraries compatible with `liboqs-python`.

## Development Notes

Code style expectations:

- Use type hints.
- Keep modules small and focused.
- Preserve clean boundaries between API, core logic, CLI, dashboard, and persistence.
- Keep cryptographic primitives in `app/core/classical` and `app/core/pqc`.
- Keep policy and simulation logic outside primitive implementations.
- Avoid hardcoded environment-specific paths; use `app/utils/config.py`.

Recommended local validation:

```bash
python -m compileall app cli dashboard tests
python -m pytest tests
```

## Extension Roadmap

High-value next steps:

- Implement full `/encrypt`, `/decrypt`, `/benchmark`, `/handshake`, `/results`, and `/export` route bodies.
- Persist benchmark and inventory results to SQLite with SQLAlchemy models.
- Connect negotiation results into the handshake simulator.
- Add ML-KEM naming alongside legacy Kyber naming.
- Add ML-DSA and SLH-DSA signature simulation.
- Add real cloud SDK inventory collectors.
- Add PKCS#11-backed HSM provider.
- Add PDF/CSV/JSON report generation.
- Add source-code crypto usage scanner for Java, Python, Go, Node, Terraform, Kubernetes, and OpenSSL configs.
- Add migration backlog export for Jira/GitHub Issues.

## Troubleshooting

### `ModuleNotFoundError: No module named pytest`

Install dependencies:

```bash
pip install -r requirements.txt
```

### `liboqs-python is not available`

Install native Open Quantum Safe libraries and `liboqs-python`, or run only the classical and non-PQC-native features.

### FastAPI TestClient import errors

Install API test dependencies:

```bash
pip install fastapi httpx
```

### Streamlit cannot import `app`

Run Streamlit from the project root:

```bash
streamlit run dashboard/app.py
```

## Security Notice

This project is a simulator and migration planning tool. It is not a drop-in production cryptographic service. Before using any cryptographic behavior in production:

- review implementation choices with a qualified cryptography engineer
- use audited libraries
- validate key management requirements
- enforce secure randomness and protected key custody
- test interoperability
- document migration exceptions and rollback paths
