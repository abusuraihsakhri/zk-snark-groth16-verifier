"""
Real tests for ZK-SNARK Groth16 Verifier Engine.
"""
import random
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from zk_snark_verifier.engine import (
    mod_pow, mod_inverse, mod_mul,
    simulated_pairing, pairing_product,
    VerificationKey, Proof,
    compute_public_input_linear_combination,
    verify_proof,
    trusted_setup, generate_valid_proof, generate_invalid_proof,
    setup_and_verify, hash_to_field,
)


class TestModularArithmetic(unittest.TestCase):

    def test_mod_pow_basic(self):
        self.assertEqual(mod_pow(2, 10, 1000), 1024 % 1000)

    def test_mod_pow_fermat(self):
        # a^(p-1) ≡ 1 (mod p) for prime p
        p = 17
        self.assertEqual(mod_pow(3, p - 1, p), 1)

    def test_mod_inverse(self):
        p = 17
        a = 5
        inv = mod_inverse(a, p)
        self.assertEqual((a * inv) % p, 1)

    def test_mod_mul(self):
        self.assertEqual(mod_mul(7, 8, 13), (56 % 13))


class TestSimulatedPairing(unittest.TestCase):

    def test_pairing_bilinear_property(self):
        # e(a1*a2, b) should equal e(a1, b)^a2 in the simulated setting
        mod = 104729
        a1, a2, b = 3, 5, 7
        # e(a1*a2, b) = g^((a1*a2)*b)
        lhs = simulated_pairing(a1 * a2, b, mod)
        # e(a1, b)^a2 = g^(a1*b*a2)
        rhs = mod_pow(simulated_pairing(a1, b, mod), a2, mod)
        self.assertEqual(lhs, rhs)

    def test_pairing_commutative_in_exponent(self):
        mod = 104729
        a, b = 11, 13
        # e(a, b) = g^(a*b) = g^(b*a) = e(b, a)
        self.assertEqual(simulated_pairing(a, b, mod), simulated_pairing(b, a, mod))

    def test_pairing_product(self):
        mod = 104729
        pairs = [(3, 5), (7, 11)]
        product = pairing_product(pairs, mod)
        # Should be g^(3*5 + 7*11) = g^(15+77) = g^92
        expected = mod_pow(2, 92, mod)
        self.assertEqual(product, expected)


class TestVerificationKey(unittest.TestCase):

    def test_to_dict_roundtrip(self):
        vk = VerificationKey(10, 20, 30, 40, [1, 2, 3], 104729)
        d = vk.to_dict()
        vk2 = VerificationKey.from_dict(d)
        self.assertEqual(vk.alpha, vk2.alpha)
        self.assertEqual(vk.beta, vk2.beta)
        self.assertEqual(vk.ic, vk2.ic)


class TestProof(unittest.TestCase):

    def test_to_dict_roundtrip(self):
        proof = Proof(100, 200, 300)
        d = proof.to_dict()
        proof2 = Proof.from_dict(d)
        self.assertEqual(proof.a, proof2.a)
        self.assertEqual(proof.b, proof2.b)
        self.assertEqual(proof.c, proof2.c)


class TestPublicInputLC(unittest.TestCase):

    def test_single_input(self):
        # L = IC[0] + x1 * IC[1]
        l = compute_public_input_linear_combination([5], [10, 3], 104729)
        self.assertEqual(l, (10 + 5 * 3) % 104729)

    def test_multiple_inputs(self):
        # L = IC[0] + x1*IC[1] + x2*IC[2]
        l = compute_public_input_linear_combination([2, 3], [1, 4, 5], 104729)
        expected = (1 + 2 * 4 + 3 * 5) % 104729
        self.assertEqual(l, expected)

    def test_zero_inputs(self):
        l = compute_public_input_linear_combination([], [42], 104729)
        self.assertEqual(l, 42)

    def test_length_mismatch_raises(self):
        with self.assertRaises(ValueError):
            compute_public_input_linear_combination([1, 2], [1], 104729)


class TestTrustedSetup(unittest.TestCase):

    def test_returns_vk_and_pk(self):
        random.seed(42)
        vk, pk = trusted_setup(104729, 1)
        self.assertIsInstance(vk, VerificationKey)
        self.assertIsInstance(pk, dict)

    def test_vk_has_correct_fields(self):
        random.seed(42)
        vk, _ = trusted_setup(104729, 2)
        self.assertEqual(len(vk.ic), 3)  # num_inputs + 1

    def test_pk_has_toxic_waste(self):
        random.seed(42)
        _, pk = trusted_setup(104729, 1)
        for key in ["alpha", "beta", "gamma", "delta", "tau"]:
            self.assertIn(key, pk)


class TestProofGeneration(unittest.TestCase):

    def test_valid_proof_verifies(self):
        random.seed(42)
        mod = 104729
        public_inputs = [42]
        vk, pk = trusted_setup(mod, 1)
        proof = generate_valid_proof(public_inputs, vk, pk)
        is_valid, details = verify_proof(proof, public_inputs, vk)
        self.assertTrue(is_valid)

    def test_valid_proof_with_multiple_inputs(self):
        random.seed(42)
        mod = 104729
        public_inputs = [10, 20, 30]
        vk, pk = trusted_setup(mod, 3)
        proof = generate_valid_proof(public_inputs, vk, pk)
        is_valid, _ = verify_proof(proof, public_inputs, vk)
        self.assertTrue(is_valid)

    def test_invalid_proof_fails(self):
        random.seed(42)
        mod = 104729
        public_inputs = [42]
        vk, _ = trusted_setup(mod, 1)
        proof = generate_invalid_proof(mod)
        is_valid, _ = verify_proof(proof, public_inputs, vk)
        # Random proof is very unlikely to verify
        self.assertFalse(is_valid)

    def test_wrong_public_inputs_fail(self):
        random.seed(42)
        mod = 104729
        public_inputs = [42]
        vk, pk = trusted_setup(mod, 1)
        proof = generate_valid_proof(public_inputs, vk, pk)
        # Verify with different public inputs
        is_valid, _ = verify_proof(proof, [99], vk)
        self.assertFalse(is_valid)


class TestVerification(unittest.TestCase):

    def test_verification_equation_structure(self):
        random.seed(42)
        mod = 104729
        vk, pk = trusted_setup(mod, 1)
        proof = generate_valid_proof([42], vk, pk)
        is_valid, details = verify_proof(proof, [42], vk)
        self.assertIn("lhs", details)
        self.assertIn("rhs", details)
        self.assertIn("L", details)
        self.assertIn("verification_equation", details)

    def test_lhs_equals_rhs_for_valid_proof(self):
        random.seed(42)
        mod = 104729
        vk, pk = trusted_setup(mod, 1)
        proof = generate_valid_proof([7], vk, pk)
        is_valid, details = verify_proof(proof, [7], vk)
        self.assertEqual(details["lhs"], details["rhs"])


class TestHashToField(unittest.TestCase):

    def test_deterministic(self):
        h1 = hash_to_field("hello", 104729)
        h2 = hash_to_field("hello", 104729)
        self.assertEqual(h1, h2)

    def test_in_field(self):
        mod = 100
        h = hash_to_field("test", mod)
        self.assertGreaterEqual(h, 0)
        self.assertLess(h, mod)

    def test_different_inputs_different_hashes(self):
        h1 = hash_to_field("abc", 104729)
        h2 = hash_to_field("def", 104729)
        self.assertNotEqual(h1, h2)


class TestSetupAndVerify(unittest.TestCase):

    def test_full_demo(self):
        random.seed(42)
        result = setup_and_verify([42], 1, 104729)
        self.assertTrue(result["verification"]["is_valid"])

    def test_demo_with_multiple_inputs(self):
        random.seed(42)
        result = setup_and_verify([1, 2, 3], 3, 104729)
        self.assertTrue(result["verification"]["is_valid"])


if __name__ == "__main__":
    unittest.main()
