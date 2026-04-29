# Post-Quantum Migration Simulator

A production-quality Python system for simulating migration from classical hybrid cryptography to post-quantum Kyber-based encryption.

## Features

- Hybrid encryption with RSA-2048 + AES-256-GCM
- PQC encryption with Kyber + AES-256-GCM
- TLS-like handshake simulation for RSA and Kyber
- Benchmark engine for key generation, encryption, decryption, ciphertext size, and throughput
- SQLite storage with SQLAlchemy ORM
- FastAPI backend API
- Streamlit dashboard with comparison charts
- Typer CLI interface
- Dockerized setup with `docker-compose`

## Repository Structure

```
post-quantum-migration-simulator/
  app/
    api/
      routes/
        crypto.py
        benchmark.py
        handshake.py
        results.py
    core/
      classical/
        rsa.py
        aes.py
      pqc/
        kyber.py
      hybrid.py
      benchmark.py
      handshake.py
    db/
      database.py
      models.py
    schemas/
      crypto.py
      benchmark.py
    utils/
      logger.py
      config.py
      serialization.py
    main.py
  dashboard/
    app.py
  cli/
    cli.py
  tests/
    test_crypto.py
    test_benchmark.py
  data/
  reports/
  requirements.txt
  Dockerfile
  docker-compose.yml
  README.md
  config.yaml
  .env
```

## Setup

### Local environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Run the API

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:

- `GET /algorithms`
- `POST /encrypt`
- `POST /decrypt`
- `POST /benchmark`
- `POST /handshake`
- `GET /results`
- `GET /export?format=json|csv`

### Run the dashboard

```bash
streamlit run dashboard/dashboard_app.py
```

### Run CLI commands

```bash
python cli/cli.py encrypt --algo rsa --input sample.txt
python cli/cli.py encrypt --algo kyber --input sample.txt
python cli/cli.py decrypt --algo rsa --payload-file sample.rsa.json --key-file sample.rsa.key
python cli/cli.py benchmark --algo rsa
python cli/cli.py handshake --mode pqc
```

### Docker

```bash
docker-compose up --build
```

- Backend: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

## Configuration

Configuration is available in `config.yaml` and `.env`:

- `DATABASE_URL`
- `ALGORITHMS_ENABLED`
- `BENCHMARK_ITERATIONS`
- `BENCHMARK_SIZES`
- `OUTPUT_PATH`
- `KYBER_MODE`
- `RSA_KEY_SIZE`

## Sample Output

```json
{
  "algorithm": "rsa",
  "mode": "classical",
  "plaintext": "SGVsbG8gd29ybGQ=",
  "message": "Use base64 decode to recover original bytes."
}
```

## Architecture

```
[Client] --> [FastAPI] --> [Crypto Engines]
                          |--> [RSA/AES Hybrid]
                          |--> [Kyber/AES Hybrid]
                          |--> [Handshake Simulator]
                          --> [SQLite via SQLAlchemy]
                          --> [Streamlit Dashboard]
```

## Testing

```bash
pytest tests/test_crypto.py tests/test_benchmark.py
```

## Notes

- The system is designed for extension to additional PQC algorithms such as Dilithium.
- All crypto outputs include metadata, timestamp, algorithm, mode, and key size.
