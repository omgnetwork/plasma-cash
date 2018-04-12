import rlp
from ethereum import utils
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer
from plasma_cash.utils.utils import get_sender
from .block import Block
from .exceptions import InvalidBlockSignatureException
from .transaction import Transaction


class ChildChain(object):

    def __init__(self, authority=plasma_config['AUTHORITY'],
                 root_chain=Deployer().get_contract('RootChain/RootChain.sol')):
        self.root_chain = root_chain
        self.authority = authority
        self.blocks = {}
        self.current_block = Block()
        self.current_block_number = 1

        # Register for deposit event listener
        deposit_filter = self.root_chain.on('Deposit')
        deposit_filter.watch(self.apply_deposit)

    def apply_deposit(self, event):
        new_owner = utils.normalize_address(event['args']['depositor'])
        amount = event['args']['amount']
        uid = event['args']['uid']
        deposit_tx = Transaction(0, uid, amount, new_owner)
        self.current_block.transaction_set.append(deposit_tx)

    def submit_block(self, sig):
        signature = bytes.fromhex(sig)
        if (signature == b'\x00' * 65 or
            get_sender(self.current_block.hash, signature) != self.authority):
            raise InvalidBlockSignatureException('failed to submit a block')

        merkle_hash = self.current_block.merkilize_transaction_set
        self.root_chain.transact({'from': '0x' + self.authority.hex()}).submitBlock(merkle_hash, self.current_block_number)
        self.blocks[self.current_block_number] = self.current_block
        self.current_block_number += 1
        self.current_block = Block()

        return merkle_hash

    def get_current_block(self):
        return rlp.encode(self.current_block).hex()
