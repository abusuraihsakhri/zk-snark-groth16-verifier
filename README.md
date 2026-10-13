# Groth16 Pairing-Equation Simulator

An educational Python and browser demonstration of a **toy Groth16-shaped verification equation**. The repository also contains a separate configurable threshold-audit workflow.

**Security scope:** This code uses modular exponentiation as a substitute for real elliptic-curve pairings. It does **not** implement genuine Groth16 proof generation or verification, R1CS/QAP constraint checking, a trustworthy setup ceremony, zero-knowledge security, post-quantum cryptography, clinical validation, or regulatory compliance. A passing result means only that the toy arithmetic identity holds.

## Browser demonstration

The standalone page is `web/index.html`; open it in a modern browser to calculate and modify toy proof examples or run local threshold checks. It works without a backend or Python. The output distinguishes arithmetic verification from a real proof, rejects malformed fields, and supports JSON export. Calculations remain local to the browser and are not sent to a remote service. **A public GitHub Pages deployment has not yet been verified.**

## Install

Requires Python 3.9 or newer.

```bash
python -m pip install -e ".[dev,server]"
python -m pytest -q
node tests/web-smoke.cjs   # optional: Node.js is needed for this browser-logic test
```

For the Python demonstration alone, `pip install -e .` is sufficient. The `server` extra provides FastAPI and Uvicorn; `dev` provides pytest.

## Toy proof CLI

```bash
python cli.py demo --public-inputs '[42]'
python cli.py setup --mod 104729 --num-inputs 1
python cli.py pairing --a 11 --b 13 --mod 104729
python cli.py lcomb --public-inputs '[5]' --ic '[10,3]'
```

The `setup` output includes demonstration parameters and must **not** be considered a secure proving key. The `verify` command accepts JSON in `--vk`, `--proof`, and `--public-inputs`; it checks the toy equation only. Python's demonstration uses prime moduli smaller than 2⁶⁴; the browser limits them to 2,147,483,647.

```python
from zk_snark_verifier.engine import setup_and_verify

result = setup_and_verify([42], num_inputs=1, mod=104729)
print(result["verification"]["is_valid"])
```

## Threshold-audit CLI and service

```bash
python -m zk_snark_verifier.cli audit --task-id TASK-001 --primary 35 --secondary 4 --status DISCORDANT_ANOMALY
python -m zk_snark_verifier.cli batch -i sample.csv -o results.csv
python -m zk_snark_verifier.cli chat "What is the system status?"
python -m zk_snark_verifier.cli serve --host 127.0.0.1 --port 8000
```

Visit `http://127.0.0.1:8000/` for the browser demonstration when running from the repository checkout. `GET /health`, `POST /api/audit` and `POST /api/chat` serve the independent threshold-audit workflow. `agents.api:app` is an additional experimental API.

The audit applies hard-coded thresholds: primary > 25, secondary > 12 or a critical flag, and selected anomaly keywords in a status descriptor. These are **illustrative rules**, not cryptographic or medical criteria. CSV values for `is_critical_flag` accept `true/false`, `1/0`, and `yes/no`.

## Container

```bash
export AUDIT_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
docker compose up --build
```

A persistent audit key must be provided by the operator. Do not commit it or include it in public web assets. The HMAC audit trail is held in memory, is not durable across restarts, and is **not** an immutable external audit ledger.

## Privacy and limitations

The static browser page performs local calculations and does not contact a remote API or store uploaded information. The Python service processes whatever is sent to it; deploy it only behind appropriate access controls. The separate `agents` framework contains regex-based identifier checks and an in-memory HMAC chain, but **regex checks are not comprehensive PHI de-identification**. Avoid sending patient data to this demonstration. No formal cryptographic security evaluation or external standards certification is claimed.

## Project layout

- `zk_snark_verifier/engine.py`: toy equation, input aggregation and modular arithmetic.
- `zk_snark_verifier/cli.py`: independent metric-based audit and CSV CLI.
- `zk_snark_verifier/server.py`: FastAPI demonstration service.
- `agents/`: experimental worker, API, and in-memory audit support.
- `web/index.html`: standalone local browser calculator and threshold demo.
- `tests/`: Python regressions and Node browser-logic smoke test.
- `enrichment.py`: illustrative feature stubs, not validated implementations.

## License

MIT. See [LICENSE](LICENSE).
