from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer
from .transaction import Transaction


class ChildChain(object):

    def __init__(self, authority=plasma_config['AUTHORITY'],
                 root_chain=Deployer().get_contract('RootChain/RootChain.sol')):
        self.root_chain = root_chain
        self.authority = authority
        self.blocks = {}
        self.current_block_number = 1

        # Register for deposit event listener
        deposit_filter = self.root_chain.on('Deposit')
        deposit_filter.watch(self.apply_deposit)

    def apply_deposit(self, event):
        print(event)
        new_owner = event['args']['depositor']
        amount = event['args']['amount']
        uid = event['args']['uid']
        deposit_tx = Transaction(0, uid, amount, new_owner)
