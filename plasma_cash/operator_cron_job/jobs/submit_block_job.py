import rlp
from ethereum import utils

from plasma_cash.child_chain.block import Block
from plasma_cash.utils.utils import sign

from .job_interface import JobInterface


class SubmitBlockJob(JobInterface):

    def __init__(self, child_chain, key):
        self.child_chain = child_chain
        self.key = utils.normalize_key(key)

    def run(self):
        block = self._get_current_block()
        sig = sign(block.hash, self.key)
        self.child_chain.submit_block(sig.hex())

    def _get_current_block(self):
        block = self.child_chain.get_current_block()
        return rlp.decode(utils.decode_hex(block), Block)
