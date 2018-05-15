import rlp
from ethereum import utils

from plasma_cash.child_chain.block import Block
from plasma_cash.child_chain.transaction import Transaction
from plasma_cash.utils.utils import sign


class Client(object):

    def __init__(self, root_chain, child_chain):
        self.root_chain = root_chain
        self.child_chain = child_chain

    def deposit(self, amount, depositor, currency):
        self.root_chain.transact({'from': depositor}).deposit(currency, amount)

    def submit_block(self, key):
        key = utils.normalize_key(key)
        block = self.get_current_block()
        sig = sign(block.hash, key)
        self.child_chain.submit_block(sig.hex())

    def send_transaction(self, prev_block, uid, amount, new_owner, key):
        new_owner = utils.normalize_address(new_owner)
        key = utils.normalize_key(key)
        tx = Transaction(prev_block, uid, amount, new_owner)
        tx.sign(key)
        self.child_chain.send_transaction(rlp.encode(tx, Transaction).hex())

    def get_current_block(self):
        block = self.child_chain.get_current_block()
        return rlp.decode(utils.decode_hex(block), Block)

    def get_block(self, blknum):
        block = self.child_chain.get_block(blknum)
        return rlp.decode(utils.decode_hex(block), Block)

    def get_tx_proof(self, blknum, uid):
        return self.child_chain.get_tx_proof(blknum, uid)
