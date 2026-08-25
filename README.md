# ZK-SNARK Groth16 Verifier (Simplified)

A pure-Python implementation of a simplified Groth16 zero-knowledge proof verifier. Uses modular arithmetic as a proxy for elliptic curve pairings. Uses only the Python standard library.

## Features

- **Simplified Groth16 Verification**: `e(A, B) = e(α, β) × e(L, γ) × e(C, δ)`
- **Simulated Pairing**: Bilinear map using modular exponentiation `e(a, b) = g^(a·b) mod p`
- **Proof Structure**: (A, B, C) proof elements
- **Verification Key**: (α, β, γ, δ, IC[]) with public input coefficients
- **Public Input Aggregation**: `L = IC[0] + Σ(xᵢ × IC[i+1])`
- **Trusted Setup**: Generate verification and proving keys
- **Proof Generation**: Construct valid proofs for testing

## CLI Usage

```bash
# Full demo: setup + prove + verify
python cli.py demo --public-inputs '[42]' --mod 104729

# Trusted setup
python cli.py setup --mod 104729 --num-inputs 2

# Verify a proof
python cli.py verify --vk '{"alpha":10,"beta":20,...}' --proof '{"a":10,"b":20,"c":30}' --public-inputs '[42]'

# Compute public input linear combination
python cli.py lcomb --public-inputs '[5]' --ic '[10, 3]' --mod 104729

# Compute simulated pairing
python cli.py pairing --a 3 --b 5 --mod 104729
```

## Python API

```python
from zk_snark_verifier.engine import (
    trusted_setup, generate_valid_proof, verify_proof, setup_and_verify
)

# Full demo
result = setup_and_verify(public_inputs=[42], num_inputs=1, mod=104729)
print(result["verification"]["is_valid"])  # True

# Step by step
vk, pk = trusted_setup(mod=104729, num_public_inputs=1)
proof = generate_valid_proof(public_inputs=[42], vk=vk, proving_key=pk)
is_valid, details = verify_proof(proof, public_inputs=[42], vk=vk)
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## License

MIT License.
