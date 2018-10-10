import rlp
from ethereum import utils
from web3.auto import w3

from plasma_cash.child_chain.block import Block
from plasma_cash.child_chain.transaction import Transaction
from plasma_cash.utils.utils import sign


class Client(object):

    def __init__(self, root_chain, child_chain, key):
        self.root_chain = root_chain
        self.child_chain = child_chain
        self.key = utils.normalize_key(key)

    @property
    def address(self):
        return w3.toChecksumAddress(utils.privtoaddr(self.key))

    def _sign_and_send_tx(self, tx):
        tx['nonce'] = w3.eth.getTransactionCount(self.address, 'pending')
        signed = w3.eth.account.signTransaction(tx, self.key)
        w3.eth.sendRawTransaction(signed.rawTransaction)

    def deposit(self, amount, currency):
        value = w3.toWei(amount, 'ether') if currency == '0x' + '00' * 20 else 0
        tx = self.root_chain.functions.deposit(currency, amount).buildTransaction(
            {'from': self.address, 'value': value}
        )
        self._sign_and_send_tx(tx)

    def submit_block(self):
        # TODO: this method should be a cron job in child chain
        block = self.get_current_block()
        sig = sign(block.hash, self.key)
        self.child_chain.submit_block(sig.hex())

    def send_transaction(self, prev_block, uid, amount, new_owner):
        new_owner = utils.normalize_address(new_owner)
        tx = Transaction(prev_block, uid, amount, new_owner)
        tx.sign(self.key)
        self.child_chain.send_transaction(rlp.encode(tx, Transaction).hex())

    def get_current_block(self):
        block = self.child_chain.get_current_block()
        return rlp.decode(utils.decode_hex(block), Block)

    def get_block(self, blknum):
        block = self.child_chain.get_block(blknum)
        return rlp.decode(utils.decode_hex(block), Block)

    def get_proof(self, blknum, uid):
        return self.child_chain.get_proof(blknum, uid)

    def start_exit(self, uid, prev_tx_blk_num, tx_blk_num):
        # TODO: Getting the whole block doesn't meet the design concept of plasma cash.
        #       Transactions and its proofs should be passed from previous owner and child chain
        #       before. When exiting, client should have enough information and only query from its
        #       databse. For now, it's just for convenience. When the exchange mechanism between
        #       clients are built, this part should be modified.
        #       issue: https://github.com/omisego/plasma-cash/issues/43
        prev_block = self.get_block(prev_tx_blk_num)
        block = self.get_block(tx_blk_num)

        prev_tx = prev_block.get_tx_by_uid(uid)
        prev_block.merklize_transaction_set()
        prev_tx_proof = prev_block.merkle.create_merkle_proof(uid)

        tx = block.get_tx_by_uid(uid)
        block.merklize_transaction_set()
        tx_proof = block.merkle.create_merkle_proof(uid)

        tx = self.root_chain.functions.startExit(
            rlp.encode(prev_tx),
            prev_tx_proof,
            prev_tx_blk_num,
            rlp.encode(tx),
            tx_proof,
            tx_blk_num
        ).buildTransaction({'from': self.address})
        self._sign_and_send_tx(tx)

    def abort_deposit(self, uid):
        tx = self.root_chain.functions.abortDeposit(uid).buildTransaction({'from': self.address})
        self._sign_and_send_tx(tx)

    def start_deposit_exit(self, uid, tx_blk_num):
        block = self.get_block(tx_blk_num)

        tx = block.get_tx_by_uid(uid)
        block.merklize_transaction_set()
        tx_proof = block.merkle.create_merkle_proof(uid)

        tx = self.root_chain.functions.startDepositExit(
            rlp.encode(tx),
            tx_proof,
            tx_blk_num
        ).buildTransaction({'from': self.address})
        self._sign_and_send_tx(tx)

    def challenge_exit(self, uid, tx_blk_num):
        block = self.get_block(tx_blk_num)

        challenge_tx = block.get_tx_by_uid(uid)
        block.merklize_transaction_set()
        tx_proof = block.merkle.create_merkle_proof(uid)

        tx = self.root_chain.functions.challengeExit(
            uid, rlp.encode(challenge_tx), tx_proof, tx_blk_num
        ).buildTransaction({'from': self.address})
        self._sign_and_send_tx(tx)

    def respond_challenge_exit(self, challenge_tx, uid, tx_blk_num):
        block = self.get_block(tx_blk_num)

        respond_tx = block.get_tx_by_uid(uid)
        block.merklize_transaction_set()
        tx_proof = block.merkle.create_merkle_proof(uid)

        tx = self.root_chain.functions.respondChallengeExit(
            uid, challenge_tx, rlp.encode(respond_tx), tx_proof, tx_blk_num
        ).buildTransaction({'from': self.address})
        self._sign_and_send_tx(tx)

    def finalize_exit(self, uid):
        tx = self.root_chain.functions.finalizeExit(uid).buildTransaction({'from': self.address})
        self._sign_and_send_tx(tx)
