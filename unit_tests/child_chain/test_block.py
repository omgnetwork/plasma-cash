import pytest

from plasma_cash.child_chain.block import Block
from plasma_cash.child_chain.transaction import Transaction


class TestBlock(object):
    DUMMY_TX_OWNER = b'\x8cT\xa4\xa0\x17\x9f$\x80\x1fI\xf92-\xab<\x87\xeb\x19L\x9b'
    UID = 1

    @pytest.fixture(scope='function')
    def block(self):
        tx = Transaction(
            prev_block=0,
            uid=self.UID,
            amount=10,
            new_owner=self.DUMMY_TX_OWNER
        )
        return Block(transaction_set=[tx])

    def test_constructor(self):
        DUMMY_TX_SET = ['tx set']
        block = Block(transaction_set=DUMMY_TX_SET)
        assert block.transaction_set == DUMMY_TX_SET
        assert block.merkle is None

    def test_constructor_with_default_param(self):
        block = Block()
        assert block.transaction_set == []
        assert block.merkle is None

    def test_hash(self, block):
        EXPECTED_HASH = (b'~\xd9\x979L.2\xb1\xa3\x1b\x81\x1e`\xa6\xddg*\xf3D\x92'
                         b'\xb6\x0f\x04\xe7f\x05\x99\x1fr\x9a\xbe\x97')
        assert block.hash == EXPECTED_HASH

    def test_merklize_transaction_set(self, block):
        EXPECTED_MERKLE_ROOT = (b'\xcfO\xbd\xb8\x92D\xb4\x8c\xacP\xedcTl\xc5k\x18\xf9\x13\xd2'
                                b'\xe6\xd3[\xe9,\xf3[\x12\xed\x1f\x97`')
        assert block.merklize_transaction_set() == EXPECTED_MERKLE_ROOT

    def test_add_tx(self, block):
        dummy_tx = Transaction(prev_block=0, uid=2, amount=10,
                               new_owner=self.DUMMY_TX_OWNER)
        block.add_tx(dummy_tx)
        assert len(block.transaction_set) == 2
        assert dummy_tx in block.transaction_set

    def test_get_tx_by_uid_tx_exists(self, block):
        tx = block.get_tx_by_uid(self.UID)
        assert tx.uid == self.UID

    def test_get_tx_by_uid_none(self, block):
        NON_EXIST_UID = 91923
        assert block.get_tx_by_uid(NON_EXIST_UID) is None
