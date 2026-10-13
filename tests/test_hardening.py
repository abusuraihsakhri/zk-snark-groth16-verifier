"""Regression tests for audit integrity, input validation and CSV ingestion."""
import csv
import json

import pytest

from agents.base import AuditTrail
from zk_snark_verifier.cli import main, parse_csv_bool
from zk_snark_verifier.engine import (
    VerificationKey, Proof, compute_public_input_linear_combination,
    mod_inverse, setup_and_verify, trusted_setup,
)


def _ledger():
    ledger = AuditTrail(secret_key="unit-test-key")
    ledger.log("test", "unit", "CHECK", {"status": "ok"})
    ledger.log("test", "unit", "CHECK2", {"status": "ok"})
    return ledger


def test_audit_signature_detects_modified_entry():
    ledger = _ledger()
    assert ledger.verify_integrity()
    ledger.logs[0]["event_type"] = "ALTERED"
    assert not ledger.verify_integrity()


def test_audit_signature_detects_modified_final_entry():
    ledger = _ledger()
    ledger.logs[-1]["payload_hash"] = "0" * 64
    assert not ledger.verify_integrity()


def test_get_trail_does_not_expose_mutable_ledger():
    ledger = _ledger()
    external = ledger.get_trail()
    external[0]["actor"] = "tamper"
    external.clear()
    assert len(ledger.get_trail()) == 2
    assert ledger.verify_integrity()


@pytest.mark.parametrize("value,expected", [
    ("true", True), ("TRUE", True), ("1", True), ("yes", True),
    ("False", False), ("0", False), ("no", False), ("", False),
])
def test_parse_csv_bool(value, expected):
    assert parse_csv_bool(value) is expected


def test_csv_bool_rejects_ambiguous_values():
    with pytest.raises(ValueError):
        parse_csv_bool("maybe")


def test_batch_false_flag_is_not_critical(tmp_path):
    input_path = tmp_path / "input.csv"
    output_path = tmp_path / "output.csv"
    with input_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "task_id", "target_identifier", "primary_metric",
            "secondary_metric", "status_descriptor", "is_critical_flag"
        ])
        writer.writeheader()
        writer.writerow({
            "task_id": "TEST-001", "target_identifier": "DEMO",
            "primary_metric": "10", "secondary_metric": "4",
            "status_descriptor": "NOMINAL", "is_critical_flag": "False"
        })
    assert main(["batch", "-i", str(input_path), "-o", str(output_path)]) == 0
    with output_path.open(encoding="utf-8", newline="") as file:
        row = next(csv.DictReader(file))
    assert row["overall_status"] == "NOMINAL_OPTIMAL"
    assert row["critical_count"] == "0"


def test_batch_rejects_nan(tmp_path):
    inp = tmp_path / "in.csv"
    inp.write_text("task_id,primary_metric,secondary_metric\nA,nan,2\n")
    with pytest.raises(ValueError, match="finite"):
        main(["batch", "-i", str(inp), "-o", str(tmp_path / "out.csv")])


@pytest.mark.parametrize("mod", [0, 1, 4, 9, 15, 104730, 2**64])
def test_toy_setup_rejects_nonprime_or_unsupported_moduli(mod):
    with pytest.raises(ValueError):
        trusted_setup(mod)


def test_noninvertible_modular_element_is_rejected():
    with pytest.raises(ValueError):
        mod_inverse(0, 17)
    with pytest.raises(ValueError):
        mod_inverse(2, 8)


def test_invalid_proof_elements_are_rejected():
    with pytest.raises(ValueError):
        Proof(True, 4, 5)
    with pytest.raises(ValueError):
        Proof(-1, 2, 3)


def test_valid_toy_demo_still_verifies():
    assert setup_and_verify([42], 1, 104729)["verification"]["is_valid"]


def test_public_input_count_validation():
    with pytest.raises(ValueError):
        compute_public_input_linear_combination([1, 2], [3], 104729)
    with pytest.raises(ValueError):
        compute_public_input_linear_combination([True], [1, 2], 104729)
