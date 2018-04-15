import rlp
from ethereum import utils
from plasma_cash.child_chain.block import Block
from plasma_cash.root_chain.deployer import Deployer
from plasma_cash.utils.utils import sign
from .child_chain_service import ChildChainService


class Client(object):

    def __init__(self,
                 root_chain=Deployer().get_contract('RootChain/RootChain.sol'),
                 child_chain=ChildChainService('http://localhost:8546')):
        self.root_chain = root_chain
        self.child_chain = child_chain

    def deposit(self, amount, depositor, currency='0x0000000000000000000000000000000000000000'):
        self.root_chain.transact({'from': depositor}).deposit(currency, amount)

    def submit_block(self, key):
        key = utils.normalize_key(key)
        block = self.get_current_block()
        sig = sign(block.hash, key)
        self.child_chain.submit_block(sig.hex())

    def get_current_block(self):
        block = self.child_chain.get_current_block()
        return rlp.decode(utils.decode_hex(block), Block)
