"""
CLI for ZK-SNARK Groth16 Verifier (Simplified).
Supports: setup, prove, verify, demo.
"""
import argparse
import json
import sys

from zk_snark_verifier.engine import (
    VerificationKey, Proof,
    verify_proof, compute_public_input_linear_combination,
    trusted_setup, generate_valid_proof, generate_invalid_proof,
    setup_and_verify, hash_to_field,
    simulated_pairing,
)


def cmd_setup(args):
    """Run trusted setup."""
    vk, pk = trusted_setup(args.mod, args.num_inputs)
    print(json.dumps({
        "verification_key": vk.to_dict(),
        "proving_key": {k: v for k, v in pk.items() if k != "alpha"},
        "note": "In production, proving key contains toxic waste and must be destroyed.",
    }, indent=2))


def cmd_verify(args):
    """Verify a proof."""
    vk = VerificationKey.from_dict(json.loads(args.vk))
    proof = Proof.from_dict(json.loads(args.proof))
    public_inputs = json.loads(args.public_inputs)
    is_valid, details = verify_proof(proof, public_inputs, vk)
    print(json.dumps(details, indent=2))


def cmd_lcomb(args):
    """Compute public input linear combination L."""
    public_inputs = json.loads(args.public_inputs)
    ic = json.loads(args.ic)
    l = compute_public_input_linear_combination(public_inputs, ic, args.mod)
    print(json.dumps({"L": l, "public_inputs": public_inputs, "ic": ic}, indent=2))


def cmd_demo(args):
    """Run full demo: setup + prove + verify."""
    public_inputs = json.loads(args.public_inputs) if args.public_inputs else [42]
    result = setup_and_verify(public_inputs, len(public_inputs), args.mod)
    print(json.dumps(result, indent=2))


def cmd_pairing(args):
    """Compute simulated pairing."""
    result = simulated_pairing(args.a, args.b, args.mod)
    print(json.dumps({"a": args.a, "b": args.b, "mod": args.mod, "pairing": result}, indent=2))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="zk-snark-groth16-verifier",
        description="ZK-SNARK Groth16 Verifier: simplified proof verification using modular arithmetic")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Setup
    p_setup = subparsers.add_parser("setup", help="Run trusted setup")
    p_setup.add_argument("--mod", type=int, default=104729, help="Prime modulus")
    p_setup.add_argument("--num-inputs", type=int, default=1, help="Number of public inputs")

    # Verify
    p_verify = subparsers.add_parser("verify", help="Verify a proof")
    p_verify.add_argument("--vk", type=str, required=True, help="Verification key JSON")
    p_verify.add_argument("--proof", type=str, required=True, help="Proof JSON")
    p_verify.add_argument("--public-inputs", type=str, required=True, help="Public inputs JSON array")

    # Linear combination
    p_lcomb = subparsers.add_parser("lcomb", help="Compute public input linear combination")
    p_lcomb.add_argument("--public-inputs", type=str, required=True, help="JSON array of public inputs")
    p_lcomb.add_argument("--ic", type=str, required=True, help="JSON array of IC coefficients")
    p_lcomb.add_argument("--mod", type=int, default=104729)

    # Demo
    p_demo = subparsers.add_parser("demo", help="Full setup + prove + verify demo")
    p_demo.add_argument("--public-inputs", type=str, default=None, help="JSON array of public inputs")
    p_demo.add_argument("--mod", type=int, default=104729)

    # Pairing
    p_pair = subparsers.add_parser("pairing", help="Compute simulated pairing")
    p_pair.add_argument("--a", type=int, required=True)
    p_pair.add_argument("--b", type=int, required=True)
    p_pair.add_argument("--mod", type=int, default=104729)

    args = parser.parse_args(argv)

    cmd_map = {
        "setup": cmd_setup,
        "verify": cmd_verify,
        "lcomb": cmd_lcomb,
        "demo": cmd_demo,
        "pairing": cmd_pairing,
    }
    return cmd_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main() or 0)
