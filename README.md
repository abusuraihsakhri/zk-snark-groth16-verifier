# ZK SNARK Groth16 Verifier

> **Domain:** Post-Quantum Cryptography & Zero-Knowledge Architecture
> **Reference Guidelines & Standards:** `NIST FIPS 203/204/205, NIST SP 800-90B & ISO/IEC Standards`

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-3776AB.svg?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688.svg?logo=fastapi&logoColor=white)
![Audit Trail](https://img.shields.io/badge/Audit-HMAC--SHA256_Tamper--Evident-brightgreen.svg)
![Zero-PHI Guard](https://img.shields.io/badge/Guard-Zero--PHI_Outbound-blue.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?logo=docker&logoColor=white)

</div>

---

## What It Does

**ZK SNARK Groth16 Verifier** is a simplified Groth16 Zero-Knowledge SNARK verification engine implementing modular arithmetic as a proxy for elliptic curve pairings. It provides:

- **Groth16 Proof Verification:** Verifies the pairing equation `e(A, B) = e(α, β) × e(L, γ) × e(C, δ)` using simulated bilinear pairings.
- **Trusted Setup Simulation:** Generates verification keys and proving keys for testing.
- **R1CS/QAP Circuit Auditing:** Multi-agent evaluation framework for constraint system analysis.
- **FastAPI REST Server:** HTTP API for remote proof verification and audit operations.

---

## Installation

```bash
pip install -e .
```

For development (with test dependencies):
```bash
pip install -e ".[dev]"
```

---

## Usage

### CLI Commands

#### Demo (Full Setup + Prove + Verify)
```bash
python cli.py demo --public-inputs '[42]'
python cli.py demo --public-inputs '[10, 20, 30]' --mod 104729
```

#### Trusted Setup
```bash
python cli.py setup --mod 104729 --num-inputs 1
```

#### Verify a Proof
```bash
python cli.py verify --vk '<verification-key-json>' --proof '<proof-json>' --public-inputs '[42]'
```

#### Compute Linear Combination
```bash
python cli.py lcomb --public-inputs '[5]' --ic '[10, 3]' --mod 104729
```

#### Simulated Pairing
```bash
python cli.py pairing --a 11 --b 13 --mod 104729
```

### Audit CLI (Multi-Agent Evaluation)
```bash
# Single task audit
python -m zk_snark_verifier.cli audit --task-id TASK-001 --primary 35.0 --secondary 4.0 --status DISCORDANT_ANOMALY

# Batch CSV processing
python -m zk_snark_verifier.cli batch -i sample.csv -o results.csv

# Supervisory chat
python -m zk_snark_verifier.cli chat "What is the system status?"

# Launch REST server
python -m zk_snark_verifier.cli serve --host 127.0.0.1 --port 8000
```

### Python API
```python
from zk_snark_verifier.engine import (
    trusted_setup, generate_valid_proof, verify_proof, setup_and_verify
)

# Full demo: setup + prove + verify
result = setup_and_verify([42], num_inputs=1, mod=104729)
print(result["verification"]["is_valid"])  # True
```

---

## Project Structure

```
zk_snark_verifier/
├── engine.py      # Core Groth16 verification engine & FrontierDomainEngine
├── models.py      # Data models (FrontierPayload, AgentTelemetryAlert)
├── agents.py      # Multi-agent coordination (ZKSNARKCoordinator)
├── cli.py         # Audit CLI interface
└── server.py      # FastAPI REST server
agents/            # Enterprise agent framework
├── base.py        # PHI guard, HMAC-SHA256 audit trail
├── models.py      # Pydantic schemas
├── supervisor.py  # System supervisor orchestrator
├── workers.py     # Domain worker agents
├── llm_factory.py # LLM provider factory
├── api.py         # FastAPI enterprise endpoints
├── learning.py    # Bayesian calibration engine
├── metrics.py     # Prometheus metrics exporter
└── streamer.py    # WebSocket telemetry broadcaster
tests/             # Test suite
enrichment.py      # Enrichment feature suite
simulator.py       # High-throughput stress testing
```

---

## Security

* **Zero-PHI Outbound Interceptor:** Active regex inspection blocking SSNs, MRNs, phone numbers, emails, and patient identifiers.
* **Tamper-Evident HMAC-SHA256 Audit Trail:** Chained, cryptographically signed logs. Set `AUDIT_SECRET_KEY` environment variable for persistent integrity across restarts.
* **PHI Redaction:** `PHIGuard.redact_phi()` sanitizes outbound text.

---

## Testing

```bash
# Run full test suite
pytest -v

# Run specific test files
pytest tests/test_zk_snark_groth16_verifier.py -v
pytest tests/test_zk_snark_verifier.py -v
pytest tests/test_enrichment.py -v
```

---

## Container Deployment

```bash
docker build -t zk-snark-groth16-verifier .
docker run -p 8000:8000 -e AUDIT_SECRET_KEY=your-secret-key zk-snark-groth16-verifier
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
