import pytest
import rlp
from mockito import mock, verify, when

from plasma_cash.child_chain.block import Block
from plasma_cash.child_chain.transaction import Transaction
from plasma_cash.operator_cron_job.jobs.submit_block_job import SubmitBlockJob
from plasma_cash.utils.utils import sign
from unit_tests.unstub_mixin import UnstubMixin


class TestSubmitBlockJob(UnstubMixin):

    @pytest.fixture(scope='function')
    def child_chain(self):
        return mock()

    def test_run(self, child_chain):
        block = self._generate_dummy_block()
        when(child_chain).get_current_block().thenReturn(rlp.encode(block).hex())

        key = (b'\xa1\x89i\x81|,\xef\xad\xf5+\x93\xeb \xf9\x17\xdc\xe7`\xce'
               b'\x13\xb2\xac\x90%\xe06\x1a\xd1\xe7\xa1\xd4H')
        job = SubmitBlockJob(child_chain, key)
        job.run()

        sig = sign(block.hash, key)
        verify(child_chain).submit_block(sig.hex())

    def _generate_dummy_block(self):
        owner = b'\x8cT\xa4\xa0\x17\x9f$\x80\x1fI\xf92-\xab<\x87\xeb\x19L\x9b'
        tx = Transaction(prev_block=0, uid=1, amount=10, new_owner=owner)
        block = Block(transaction_set=[tx])
        return block
