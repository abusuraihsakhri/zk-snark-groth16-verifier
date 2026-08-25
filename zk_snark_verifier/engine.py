"""
ZK-SNARK Groth16 Verifier Engine (Simplified)
Implements a simplified Groth16 verification using modular arithmetic as a proxy
for elliptic curve pairings. The verification equation is:
    e(A, B) = e(α, β) × e(L, γ) × e(C, δ)
Where A, B are proof elements, L is the linear combination of public inputs,
and α, β, γ, δ are verification key elements.

Uses only Python stdlib.
"""
import hashlib
import json
import random
from typing import List, Dict, Any, Tuple, Optional


# ---------------------------------------------------------------------------
# Modular arithmetic utilities
# ---------------------------------------------------------------------------

def mod_pow(base: int, exp: int, mod: int) -> int:
    """Modular exponentiation."""
    return pow(base, exp, mod)


def mod_inverse(a: int, mod: int) -> int:
    """Modular inverse using Fermat's little theorem (mod must be prime)."""
    return pow(a, mod - 2, mod)


def mod_mul(a: int, b: int, mod: int) -> int:
    """Modular multiplication."""
    return (a * b) % mod


# ---------------------------------------------------------------------------
# Simulated pairing function
# ---------------------------------------------------------------------------

def simulated_pairing(a: int, b: int, mod: int) -> int:
    """
    Simulate a bilinear pairing e(a, b) using modular arithmetic.
    In a real implementation, this would use elliptic curve pairings
    (e.g., ate pairing on BN254). Here we use:
        e(a, b) = g^(a*b) mod p
    where g is a generator. This preserves the bilinear property:
        e(a1*a2, b) = e(a1, b)^a2 = e(a2, b)^a1
    """
    g = 2  # generator
    return mod_pow(g, (a * b), mod)


def pairing_product(pairs: List[Tuple[int, int]], mod: int) -> int:
    """
    Compute product of multiple pairings: Π e(a_i, b_i) mod p.
    In the simulated setting: g^(Σ a_i*b_i) mod p.
    """
    g = 2
    total_exp = sum(a * b for a, b in pairs)
    return mod_pow(g, total_exp, mod)


# ---------------------------------------------------------------------------
# Verification Key
# ---------------------------------------------------------------------------

class VerificationKey:
    """
    Groth16 verification key: (α, β, γ, δ, IC[])
    IC is the array of coefficients for the linear combination of public inputs.
    """

    def __init__(self, alpha: int, beta: int, gamma: int, delta: int,
                 ic: List[int], mod: int):
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.delta = delta
        self.ic = ic  # IC[0], IC[1], ..., IC[m] for m public inputs
        self.mod = mod

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alpha": self.alpha,
            "beta": self.beta,
            "gamma": self.gamma,
            "delta": self.delta,
            "ic": self.ic,
            "mod": self.mod,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "VerificationKey":
        return cls(d["alpha"], d["beta"], d["gamma"], d["delta"],
                   d["ic"], d["mod"])


# ---------------------------------------------------------------------------
# Proof
# ---------------------------------------------------------------------------

class Proof:
    """Groth16 proof: (A, B, C) elements."""

    def __init__(self, a: int, b: int, c: int):
        self.a = a
        self.b = b
        self.c = c

    def to_dict(self) -> Dict[str, Any]:
        return {"a": self.a, "b": self.b, "c": self.c}

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Proof":
        return cls(d["a"], d["b"], d["c"])


# ---------------------------------------------------------------------------
# Public Input Aggregation
# ---------------------------------------------------------------------------

def compute_public_input_linear_combination(public_inputs: List[int],
                                             ic: List[int], mod: int) -> int:
    """
    Compute L = IC[0] + Σ(xᵢ × IC[i+1]) mod p.
    
    Args:
        public_inputs: The public input values x₁, x₂, ..., xₘ
        ic: Verification key IC coefficients [IC[0], IC[1], ..., IC[m]]
        mod: Prime modulus
    
    Returns:
        L = IC[0] + x₁×IC[1] + x₂×IC[2] + ... + xₘ×IC[m] mod p
    """
    if len(public_inputs) + 1 != len(ic):
        raise ValueError(
            f"IC length ({len(ic)}) must be num_public_inputs + 1 ({len(public_inputs) + 1})")

    l = ic[0] % mod
    for i, x in enumerate(public_inputs):
        l = (l + x * ic[i + 1]) % mod
    return l


# ---------------------------------------------------------------------------
# Groth16 Verification
# ---------------------------------------------------------------------------

def verify_proof(proof: Proof, public_inputs: List[int],
                  vk: VerificationKey) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify a Groth16 proof.
    
    Verification equation:
        e(A, B) = e(α, β) × e(L, γ) × e(C, δ)
    
    In the simulated pairing setting:
        g^(A*B) = g^(α*β + L*γ + C*δ) mod p
    Which simplifies to:
        A*B ≡ α*β + L*γ + C*δ (mod order)
    
    Args:
        proof: The proof (A, B, C)
        public_inputs: Public input values
        vk: Verification key
    
    Returns:
        Tuple of (is_valid, details_dict)
    """
    mod = vk.mod

    # Compute L = IC[0] + Σ(xᵢ × IC[i+1])
    l = compute_public_input_linear_combination(public_inputs, vk.ic, mod)

    # Left side: e(A, B)
    lhs = simulated_pairing(proof.a, proof.b, mod)

    # Right side: e(α, β) × e(L, γ) × e(C, δ)
    # In simulated setting: g^(α*β + L*γ + C*δ)
    rhs_exp = (vk.alpha * vk.beta + l * vk.gamma + proof.c * vk.delta) % (mod - 1)
    rhs = mod_pow(2, rhs_exp, mod)

    is_valid = lhs == rhs

    details = {
        "is_valid": is_valid,
        "lhs": lhs,
        "rhs": rhs,
        "L": l,
        "public_inputs": public_inputs,
        "proof": proof.to_dict(),
        "verification_equation": "e(A, B) = e(α, β) × e(L, γ) × e(C, δ)",
    }

    return is_valid, details


# ---------------------------------------------------------------------------
# Trusted Setup (for testing/demo)
# ---------------------------------------------------------------------------

def trusted_setup(mod: int, num_public_inputs: int = 1,
                   secret: Optional[int] = None) -> Tuple[VerificationKey, Dict[str, int]]:
    """
    Simplified trusted setup for testing.
    In a real Groth16 setup, this involves toxic waste (α, β, γ, δ, τ).
    Here we generate random values.
    
    Returns:
        Tuple of (verification_key, proving_key_params)
    """
    if secret is None:
        secret = random.randrange(2, mod - 1)

    # Generate toxic waste
    alpha = random.randrange(2, mod - 1)
    beta = random.randrange(2, mod - 1)
    gamma = random.randrange(2, mod - 1)
    delta = random.randrange(2, mod - 1)
    tau = secret  # evaluation point

    # Generate IC coefficients
    ic = [random.randrange(0, mod) for _ in range(num_public_inputs + 1)]

    vk = VerificationKey(alpha, beta, gamma, delta, ic, mod)

    proving_key = {
        "alpha": alpha,
        "beta": beta,
        "gamma": gamma,
        "delta": delta,
        "tau": tau,
        "ic": ic,
    }

    return vk, proving_key


def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended Euclidean Algorithm: returns (g, x, y) such that a*x + b*y = g."""
    if a == 0:
        return b, 0, 1
    g, x, y = _extended_gcd(b % a, a)
    return g, y - (b // a) * x, x


def _mod_inverse_general(a: int, m: int) -> int:
    """Modular inverse using extended GCD (works for non-prime moduli)."""
    g, x, _ = _extended_gcd(a % m, m)
    if g != 1:
        raise ValueError(f"No modular inverse: gcd({a}, {m}) = {g}")
    return x % m


def generate_valid_proof(public_inputs: List[int], vk: VerificationKey,
                          proving_key: Dict[str, int]) -> Proof:
    """
    Generate a valid proof for given public inputs (for testing).
    In a real prover, this involves computing over the CRS.
    Here we construct A, B, C such that the verification equation holds.
    """
    mod = vk.mod
    alpha = proving_key["alpha"]
    beta = proving_key["beta"]
    gamma = proving_key["gamma"]
    delta = proving_key["delta"]

    # Compute L
    l = compute_public_input_linear_combination(public_inputs, vk.ic, mod)

    # We need: A*B = α*β + L*γ + C*δ (mod mod-1)
    # Choose A = α, B = β, then we need C such that:
    # α*β = α*β + L*γ + C*δ => C*δ = -L*γ => C = -L*γ * δ^(-1)
    a = alpha
    b = beta
    modulus = mod - 1
    target = (-l * gamma) % modulus
    try:
        delta_inv = _mod_inverse_general(delta % modulus, modulus)
        c = (target * delta_inv) % modulus
    except ValueError:
        # If delta is not invertible, use a different construction
        # Choose A = 1, B = α*β + L*γ + C*δ, pick C freely
        c = 1
        a = 1
        b = (alpha * beta + l * gamma + c * delta) % modulus

    return Proof(a, b, c)


def generate_invalid_proof(mod: int) -> Proof:
    """Generate a random (likely invalid) proof for testing."""
    return Proof(
        random.randrange(2, mod - 1),
        random.randrange(2, mod - 1),
        random.randrange(2, mod - 1),
    )


# ---------------------------------------------------------------------------
# High-level API
# ---------------------------------------------------------------------------

def setup_and_verify(public_inputs: List[int], num_inputs: int = 1,
                      mod: int = 104729) -> Dict[str, Any]:
    """
    Full setup + proof generation + verification for demonstration.
    """
    vk, pk = trusted_setup(mod, num_inputs)
    proof = generate_valid_proof(public_inputs, vk, pk)
    is_valid, details = verify_proof(proof, public_inputs, vk)

    return {
        "setup": {
            "mod": mod,
            "num_public_inputs": num_inputs,
            "vk": vk.to_dict(),
        },
        "proof": proof.to_dict(),
        "verification": details,
    }


def hash_to_field(data: str, mod: int) -> int:
    """Hash a string to a field element."""
    h = hashlib.sha256(data.encode()).hexdigest()
    return int(h, 16) % mod
