import rlp
from ethereum import utils

from plasma_cash.utils.utils import get_sender

from .block import Block
from .exceptions import (InvalidBlockSignatureException,
                         InvalidTxSignatureException,
                         PreviousTxNotFoundException, TxAlreadySpentException,
                         TxAmountMismatchException)
from .transaction import Transaction


class ChildChain(object):

    def __init__(self, authority, root_chain, db):
        self.root_chain = root_chain
        self.authority = authority
        self.db = db
        self.current_block = Block()
        self.current_block_number = self.db.get_current_block_num()

        # Register for deposit event listener
        deposit_filter = self.root_chain.on('Deposit')
        deposit_filter.watch(self.apply_deposit)

    def apply_deposit(self, event):
        new_owner = utils.normalize_address(event['args']['depositor'])
        amount = event['args']['amount']
        uid = event['args']['uid']
        deposit_tx = Transaction(0, uid, amount, new_owner)
        self.current_block.add_tx(deposit_tx)

    def submit_block(self, sig):
        signature = bytes.fromhex(sig)
        if (signature == b'\x00' * 65 or
           get_sender(self.current_block.hash, signature) != self.authority):
            raise InvalidBlockSignatureException('failed to submit a block')

        merkle_hash = self.current_block.merklize_transaction_set()

        self.root_chain.transact(
            {'from': '0x' + self.authority.hex()}
        ).submitBlock(merkle_hash, self.current_block_number)

        self.db.save_block(self.current_block, self.current_block_number)
        self.current_block_number = self.db.increment_current_block_num()
        self.current_block = Block()

        return merkle_hash

    def apply_transaction(self, transaction):
        tx = rlp.decode(utils.decode_hex(transaction), Transaction)

        prev_tx = self.db.get_block(tx.prev_block).get_tx_by_uid(tx.uid)
        if prev_tx is None:
            raise PreviousTxNotFoundException('failed to apply transaction')
        if prev_tx.spent:
            raise TxAlreadySpentException('failed to apply transaction')
        if prev_tx.amount != tx.amount:
            raise TxAmountMismatchException('failed to apply transaction')
        if tx.sig == b'\x00' * 65 or tx.sender != prev_tx.new_owner:
            raise InvalidTxSignatureException('failed to apply transaction')

        prev_tx.spent = True  # Mark the previous tx as spent
        self.current_block.add_tx(tx)
        return tx.hash

    def get_current_block(self):
        return rlp.encode(self.current_block).hex()

    def get_block(self, blknum):
        block = self.db.get_block(blknum)
        return rlp.encode(block).hex()

    def get_proof(self, blknum, uid):
        block = self.db.get_block(blknum)
        return block.merkle.create_merkle_proof(uid)
