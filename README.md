# Post-Quantum Migration Simulator

A production-quality Python platform for simulating and planning migration from classical RSA/ECC hybrid cryptography to post-quantum Kyber-based encryption. The system combines hands-on cryptographic workflows, cloud and on-prem crypto inventory scanning, PQC readiness scoring, NIST-aligned migration profiles, TLS-style algorithm negotiation, and HSM simulation under a single FastAPI backend with a Streamlit dashboard and Typer CLI.

## Features

- **Hybrid encryption** — RSA-2048 + AES-256-GCM and Kyber + AES-256-GCM side-by-side
- **TLS-like handshake simulation** — classical RSA key exchange vs Kyber KEM
- **Benchmark engine** — key generation, encryption, decryption, ciphertext size, and throughput
- **Crypto inventory scanner** — AWS, Azure, GCP, and on-prem file-based discovery
- **PQC readiness scoring** — per-asset risk and readiness scoring with recommended actions
- **NIST migration profiles** — baseline, hybrid_transition, pqc_preferred, strict_pqc
- **Algorithm negotiation** — TLS-style handshake negotiation with profile enforcement
- **Software HSM simulator** — key generation and key wrapping abstraction
- **FastAPI backend** — typed routes with Pydantic response models and rate limiting
- **Streamlit dashboard** — benchmark and handshake comparison charts
- **Typer CLI** — encrypt, decrypt, benchmark, and handshake commands
- **SQLite storage** — results persisted via SQLAlchemy ORM
- **Docker** — single `docker-compose up` runs the full stack

## Architecture

```
[Client / CLI]
      |
      v
[FastAPI Backend — app/main.py]
      |
      +--[Crypto Routes]--------> RSAHybridCipher | KyberHybridCipher
      |                           HandshakeSimulator | BenchmarkEngine
      |
      +--[Inventory Routes]-----> InventoryScanner (AWS/Azure/GCP/on-prem)
      |                           ReadinessScorer
      |
      +--[Migration Routes]-----> NistProfiles | AlgorithmNegotiator | HSMSimulator
      |
      +--[Results Routes]-------> SQLite (via SQLAlchemy)
      |
      v
[Streamlit Dashboard]       [Typer CLI]
```

## Repository Structure

```
post-quantum-migration-simulator/
  app/
    api/
      routes/
        crypto.py         — encrypt, decrypt, list algorithms
        benchmark.py      — run benchmarks, store results
        handshake.py      — classical and PQC handshake simulation
        results.py        — query and export stored results
        inventory.py      — crypto asset inventory and readiness
        migration.py      — profiles, negotiation, HSM operations
    core/
      classical/
        rsa.py            — RSA-2048 key gen, OAEP encrypt/decrypt
        aes.py            — AES-256-GCM encrypt/decrypt
      pqc/
        kyber.py          — Kyber KEM via liboqs, HKDF key derivation
      hybrid.py           — RSAHybridCipher and KyberHybridCipher facades
      handshake.py        — classical and PQC handshake simulators
      benchmark.py        — keygen/encrypt/decrypt timing and throughput
      inventory.py        — cloud and on-prem crypto asset scanner
      readiness.py        — per-asset risk and readiness scoring
      profiles.py         — NIST PQC migration profile definitions
      negotiation.py      — TLS-style algorithm negotiation engine
      hsm.py              — software HSM simulator
      interfaces.py       — shared abstract base types
    db/
      database.py         — SQLAlchemy engine, session, Base
      models.py           — BenchmarkResult, HandshakeResult ORM models
    schemas/
      crypto.py           — EncryptResponse, DecryptResponse
      benchmark.py        — BenchmarkResultSchema, HandshakeResultSchema
      inventory.py        — InventoryScanResponse, ReadinessReportResponse
      migration.py        — negotiation, profile, and HSM request/response schemas
    utils/
      config.py           — YAML + dotenv settings loader
      logger.py           — rotating file + console logger (lazy init)
      serialization.py    — base64 encode/decode helpers
      limiter.py          — slowapi rate limiter
    main.py
  dashboard/
    dashboard_app.py      — Streamlit benchmark and handshake dashboard
  cli/
    cli.py                — Typer CLI (encrypt, decrypt, benchmark, handshake)
  tests/
    test_crypto.py        — RSA/Kyber encrypt-decrypt, error cases
    test_benchmark.py     — benchmark engine correctness and edge cases
    test_inventory.py     — inventory scanner
    test_readiness.py     — readiness scoring
    test_migration_profiles.py — NIST profile lookup and negotiation
    test_api_integration.py    — FastAPI route integration tests
  data/
    aws_inventory.json    — sample AWS crypto asset inventory
    azure_inventory.json  — sample Azure crypto asset inventory
    gcp_inventory.json    — sample GCP crypto asset inventory
    on_prem/              — sample on-prem PEM files
  reports/                — log and report output directory
  config.yaml             — default configuration
  .env                    — environment overrides (not committed)
  requirements.txt
  Dockerfile
  docker-compose.yml
```

## Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Kyber operations require native `liboqs` libraries. If unavailable, all classical, inventory, readiness, negotiation, HSM, and dashboard features work without it.

## Configuration

Settings are loaded from `config.yaml` first, then overridden by `.env`. All keys are optional and fall back to the defaults shown.

`config.yaml` / `.env` key | Default | Description
---|---|---
`DATABASE_URL` | `sqlite:///./data/results.db` | SQLAlchemy database URL
`ALGORITHMS_ENABLED` | `rsa,kyber` | Comma-separated list of enabled algorithms
`BENCHMARK_ITERATIONS` | `3` | Repetitions per file size in a benchmark run
`BENCHMARK_SIZES` | `1024,1048576,10485760` | File sizes (bytes) to benchmark
`OUTPUT_PATH` | `./reports` | Directory for log files
`KYBER_MODE` | `Kyber512` | liboqs KEM variant (`Kyber512`, `Kyber768`, `Kyber1024`)
`RSA_KEY_SIZE` | `2048` | RSA key size in bits

## Running the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Interactive docs: `http://localhost:8000/docs`

## API Endpoints

### Crypto

| Method | Path | Description |
|---|---|---|
| `GET` | `/algorithms` | List enabled algorithms |
| `POST` | `/encrypt?algorithm=rsa\|kyber` | Encrypt an uploaded file; returns base64 payload + key |
| `POST` | `/decrypt` | Decrypt a payload with the matching private key |

`/encrypt` is rate-limited to **20 requests/minute** per IP.

**Decrypt request body:**
```json
{
  "algorithm": "rsa",
  "private_key": "<base64-encoded private key>",
  "payload": {
    "ciphertext": "...",
    "nonce": "...",
    "encrypted_key": "..."
  }
}
```

### Benchmark

| Method | Path | Description |
|---|---|---|
| `POST` | `/benchmark?algorithm=rsa\|kyber` | Run keygen + encrypt + decrypt benchmark, store results |
| `GET` | `/results` | Retrieve stored benchmark and handshake results |
| `GET` | `/export?fmt=json\|csv` | Export all results as JSON or CSV |

`/benchmark` is rate-limited to **5 requests/minute** per IP.

### Handshake

| Method | Path | Description |
|---|---|---|
| `POST` | `/handshake?mode=classical\|pqc` | Simulate a TLS-like key exchange handshake |

### Inventory & Readiness

| Method | Path | Description |
|---|---|---|
| `POST` | `/inventory/scan` | Scan all configured environments for crypto assets |
| `GET` | `/inventory/environments` | Return the current inventory |
| `GET` | `/readiness` | Return per-asset PQC readiness and risk assessment |

### Migration Planning

| Method | Path | Description |
|---|---|---|
| `GET` | `/profiles` | List all NIST PQC migration profiles |
| `POST` | `/negotiate` | Run TLS-style algorithm negotiation between client and server |
| `POST` | `/hsm/keys` | Generate a key in the software HSM |
| `POST` | `/hsm/wrap` | Wrap a key using the software HSM |

**Negotiate request body:**
```json
{
  "profile": "hybrid_transition",
  "client": {
    "key_exchange_algorithms": ["x25519+ml-kem-768", "x25519"],
    "signature_algorithms": ["ecdsa-p256-sha256", "ml-dsa-65"]
  },
  "server": {
    "key_exchange_algorithms": ["x25519+ml-kem-768", "ecdhe-p256"],
    "signature_algorithms": ["ecdsa-p256-sha256"]
  }
}
```

## Running the Dashboard

```bash
streamlit run dashboard/dashboard_app.py
```

Opens at `http://localhost:8501`. Tabs:

- **Overview** — record counts and median throughput by algorithm
- **RSA vs PQC** — encrypt latency and throughput bar/line charts
- **Handshake** — latency and payload size comparison
- **Detailed metrics** — raw data tables

Run at least one `/benchmark` and one `/handshake` request first to populate the charts.

## CLI

All commands are run from the project root.

```bash
python cli/cli.py --help
```

### Encrypt a file

```bash
python cli/cli.py encrypt rsa sample.txt
python cli/cli.py encrypt kyber sample.txt --output sample.kyber.json
```

Writes `sample.rsa.json` (encrypted payload) and `sample.rsa.key` (base64 private key). Keep the `.key` file — it is required for decryption.

### Decrypt a file

```bash
python cli/cli.py decrypt rsa sample.rsa.json sample.rsa.key
python cli/cli.py decrypt kyber sample.kyber.json sample.kyber.key
```

The private key is read from a file rather than passed on the command line, to prevent exposure in shell history and process listings.

### Run a benchmark

```bash
python cli/cli.py benchmark rsa
python cli/cli.py benchmark kyber
```

### Simulate a handshake

```bash
python cli/cli.py handshake         # PQC (default)
python cli/cli.py handshake --mode classical
```

## Docker

```bash
docker-compose up --build
```

| Service | URL |
|---|---|
| FastAPI backend | `http://localhost:8000` |
| Streamlit dashboard | `http://localhost:8501` |

## Testing

```bash
pytest tests/
```

Run a specific suite:

```bash
pytest tests/test_crypto.py          # RSA/Kyber encrypt-decrypt, error cases
pytest tests/test_benchmark.py       # benchmark engine
pytest tests/test_inventory.py       # inventory scanner
pytest tests/test_readiness.py       # readiness scoring
pytest tests/test_migration_profiles.py  # NIST profiles and negotiation
pytest tests/test_api_integration.py # FastAPI routes (requires httpx)
```

## Crypto Inventory Input Format

Inventory files (`data/aws_inventory.json`, `data/azure_inventory.json`, `data/gcp_inventory.json`) are JSON arrays:

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

Field | Values
---|---
`asset_type` | `key`, `certificate`, `cert`
`exposure` | `public`, `internal`, `private`, `unknown`
`criticality` | `critical`, `high`, `medium`, `low`

On-prem scanning reads files under `data/on_prem/` and detects PEM markers and common key/cert extensions (`.pem`, `.key`, `.p12`, `.crt`, etc.).

## NIST Migration Profiles

Profile | Description
---|---
`baseline` | Inventory and benchmark existing classical crypto; no migration yet
`hybrid_transition` | Require hybrid classical + PQC negotiation; classical-only is rejected
`pqc_preferred` | Prefer standardized PQC with hybrid fallback allowed
`strict_pqc` | PQC-only; no classical algorithms permitted

## Security Notes

- **Rate limiting** — `/encrypt` is limited to 20 req/min and `/benchmark` to 5 req/min per IP to prevent resource exhaustion.
- **Private key handling** — the `/encrypt` endpoint generates an ephemeral keypair and returns the private key in the response for simulator use. In production, key management must be handled separately.
- **CLI key files** — the `decrypt` command reads the private key from a file (`--key-file`) rather than accepting it as a command-line argument, preventing exposure in shell history.
- **Cryptographic randomness** — all nonces, session keys, and pre-master secrets use `os.urandom`.
- **AEAD integrity** — AES-256-GCM authentication tags are verified on every decryption; tampered ciphertext raises an error returned as HTTP 400.
- This project is a simulation and planning tool, not a production cryptographic service. Review all cryptographic choices with a qualified engineer before any production use.
