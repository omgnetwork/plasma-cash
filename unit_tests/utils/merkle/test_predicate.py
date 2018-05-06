from ethereum.utils import sha3

from plasma_cash.utils.merkle.predicate import is_valid_proof


class TestPredicate(object):

    def test_proof_is_valid(self):
        # Assume: leaves = {0: dummy_val, 1: dummy_val, 2: empty_val, 3: dummy_val}
        empty_val = b'\x00' * 32
        dummy_val = b'\x01' * 32
        mid_left_val = sha3(dummy_val + dummy_val)
        mid_right_val = sha3(empty_val + dummy_val)
        root = sha3(mid_left_val + mid_right_val)
        assert is_valid_proof(leaf=dummy_val, uid=0, proof=dummy_val + mid_right_val, root=root)
        assert is_valid_proof(leaf=dummy_val, uid=1, proof=dummy_val + mid_right_val, root=root)
        assert is_valid_proof(leaf=empty_val, uid=2, proof=dummy_val + mid_left_val, root=root)
        assert is_valid_proof(leaf=dummy_val, uid=3, proof=empty_val + mid_left_val, root=root)

    def test_proof_is_invalid(self):
        # Assume: leaves = {0: dummy_val, 1: dummy_val, 2: dummy_val, 3: empty_val}
        empty_val = b'\x00' * 32
        dummy_val = b'\x01' * 32
        mid_left_val = sha3(dummy_val + dummy_val)
        mid_right_val = sha3(dummy_val + empty_val)
        root = sha3(mid_left_val + mid_right_val)
        # the proof of leaf 0 should be `dummy_val + mid_right_val`
        assert not is_valid_proof(leaf=dummy_val, uid=0, proof=dummy_val + mid_left_val, root=root)
        # leaf 3 should be empty leaf
        assert not is_valid_proof(leaf=dummy_val, uid=3, proof=dummy_val + mid_left_val, root=root)
