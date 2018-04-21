import pytest
import rlp
from ethereum import utils as eth_utils
from mockito import any, mock, verify, when

from plasma_cash.child_chain.block import Block
from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.child_chain.exceptions import InvalidBlockSignatureException


class TestChildChain(object):
    DUMMY_AUTHORITY = b"\x14\x7f\x08\x1b\x1a6\xa8\r\xf0Y\x15(ND'\xc1\xf6\xdd\x98\x84"
    DUMMY_SIG = '01' * 65  # sig for DUMMY_AUTHORITY
    ROOT_CHAIN = mock()

    @pytest.fixture(scope='function')
    def child_chain(self):
        deposit_filter = mock()
        when(self.ROOT_CHAIN).on('Deposit').thenReturn(deposit_filter)
        return ChildChain(authority=self.DUMMY_AUTHORITY,
                          root_chain=self.ROOT_CHAIN)

    def test_constructor(self):
        deposit_filter = mock()
        when(self.ROOT_CHAIN).on('Deposit').thenReturn(deposit_filter)

        ChildChain(authority=self.DUMMY_AUTHORITY, root_chain=self.ROOT_CHAIN)

        verify(self.ROOT_CHAIN).on('Deposit')
        verify(deposit_filter).watch(any)

    def test_apply_deposit(self, child_chain):
        DUMMY_AMOUT = 123
        DUMMY_UID = 'dummy uid'
        DUMMY_ADDR = b'\xfd\x02\xec\xeeby~u\xd8k\xcf\xf1d.\xb0\x84J\xfb(\xc7'

        event = {'args': {
            'amount': DUMMY_AMOUT,
            'uid': DUMMY_UID,
            'depositor': DUMMY_ADDR,
        }}

        child_chain.apply_deposit(event)

        tx = child_chain.current_block.transaction_set[0]
        assert tx.amount == DUMMY_AMOUT
        assert tx.uid == DUMMY_UID
        assert tx.new_owner == eth_utils.normalize_address(DUMMY_ADDR)

    def test_submit_block(self, child_chain):
        DUMMY_MERKLE = 'merkle hash'
        MOCK_TRANSACT = mock()

        block_number = child_chain.current_block_number
        block = child_chain.current_block
        when(child_chain.current_block).merklize_transaction_set().thenReturn(DUMMY_MERKLE)
        when(self.ROOT_CHAIN).transact(any).thenReturn(MOCK_TRANSACT)

        child_chain.submit_block(self.DUMMY_SIG)

        verify(MOCK_TRANSACT).submitBlock(DUMMY_MERKLE, block_number)
        assert child_chain.current_block_number == block_number + 1
        assert child_chain.blocks[block_number] == block
        assert child_chain.current_block == Block()

    def test_submit_block_with_invalid_sig(self, child_chain):
        INVALID_SIG = '11' * 65
        with pytest.raises(InvalidBlockSignatureException):
            child_chain.submit_block(INVALID_SIG)

    def test_submit_block_with_empty_sig(self, child_chain):
        EMPTY_SIG = '00' * 65
        with pytest.raises(InvalidBlockSignatureException):
            child_chain.submit_block(EMPTY_SIG)

    def test_get_current_block(self, child_chain):
        expected = rlp.encode(child_chain.current_block).hex()
        assert expected == child_chain.get_current_block()
