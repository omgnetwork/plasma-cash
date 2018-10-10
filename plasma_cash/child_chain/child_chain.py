import time
from threading import Thread

import rlp
from ethereum import utils
from web3.auto import w3

from plasma_cash.utils.utils import get_sender, sign

from .block import Block
from .event import emit
from .exceptions import (DepositAlreadyAppliedException, InvalidBlockNumException,
                         InvalidBlockSignatureException, InvalidTxSignatureException,
                         PreviousTxNotFoundException, TxAlreadySpentException,
                         TxAmountMismatchException, TxWithSameUidAlreadyExists)
from .transaction import Transaction


class ChildChain(object):

    def __init__(self, key, root_chain, db):
        self.key = utils.normalize_key(key)
        self.authority = utils.privtoaddr(self.key)
        self.root_chain = root_chain
        self.db = db
        self.current_block = Block()
        self.current_block_number = self.db.get_current_block_num()

        """
        TODO: should be removed as there's operator cron job that's doing the job
        here. Temperary keep this to not break integration test.
        """
        deposit_filter = self.root_chain.eventFilter('Deposit', {'fromBlock': 0})
        worker = Thread(target=self.log_loop, args=(deposit_filter, 0.1), daemon=True)
        worker.start()

    def log_loop(self, event_filter, poll_interval):
        """
        TODO: should be removed as there's operator cron job that's doing the job
        here. Temperary keep this to not break integration test.
        """
        while True:
            for event in event_filter.get_new_entries():
                depositor = event['args']['depositor']
                amount = event['args']['amount']
                uid = event['args']['uid']
                self.apply_deposit(depositor, amount, uid)
            time.sleep(poll_interval)

    def apply_deposit(self, depositor, amount, uid):
        new_owner = utils.normalize_address(depositor)

        if not self.current_block.get_tx_by_uid(uid):
            deposit_tx = Transaction(0, uid, amount, new_owner)
            self.current_block.add_tx(deposit_tx)
            sig = sign(self.current_block.hash, self.key)
            self.submit_block(sig.hex(), True, uid)
            return deposit_tx.hash

        err_msg = 'deposit of uid: {} is already applied previously'.format(uid)
        raise DepositAlreadyAppliedException(err_msg)

    def submit_block(self, sig, isDepositBlock=False, uid=None):
        signature = bytes.fromhex(sig)
        if (signature == b'\x00' * 65 or
           get_sender(self.current_block.hash, signature) != self.authority):
            raise InvalidBlockSignatureException('failed to submit a block')

        merkle_hash = self.current_block.merklize_transaction_set()
        deposit_tx, deposit_tx_proof = b'', b''
        if uid is not None:
            deposit_tx = self.current_block.get_tx_by_uid(uid)
            deposit_tx_proof = self.current_block.merkle.create_merkle_proof(uid)

        authority_address = w3.toChecksumAddress('0x' + self.authority.hex())
        tx = self.root_chain.functions.submitBlock(
            merkle_hash,
            self.current_block_number,
            isDepositBlock,
            rlp.encode(deposit_tx),
            deposit_tx_proof
        ).buildTransaction({
            'from': authority_address,
            'nonce': w3.eth.getTransactionCount(authority_address, 'pending')
        })

        signed = w3.eth.account.signTransaction(tx, self.key)
        w3.eth.sendRawTransaction(signed.rawTransaction)

        emit('chain.block', self.current_block_number)
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
        if self.current_block.get_tx_by_uid(tx.uid):
            raise TxWithSameUidAlreadyExists('failed to apply transaction')

        prev_tx.spent = True  # Mark the previous tx as spent
        self.current_block.add_tx(tx)
        return tx.hash

    def get_current_block(self):
        return rlp.encode(self.current_block).hex()

    def get_block(self, blknum):
        if 0 < blknum < self.current_block_number:
            block = self.db.get_block(blknum)
        elif blknum == self.current_block_number:
            return self.get_current_block()
        else:
            raise InvalidBlockNumException(
                'current blockNum is {}, your requested blocknum does not exists'.format(
                    self.current_block_number))
        return rlp.encode(block).hex()

    def get_proof(self, blknum, uid):
        block = self.db.get_block(blknum)
        return block.merkle.create_merkle_proof(uid)
