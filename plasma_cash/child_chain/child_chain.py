class ChildChain(object):

    def __init__(self, authority, root_chain):
        self.root_chain = root_chain
        self.authority = authority
        self.blocks = {}
        self.current_block_number = 1

        # Register for deposit event listener
        deposit_filter = self.root_chain.on('Deposit')
        deposit_filter.watch(self.apply_deposit)

    def apply_deposit(self, event):
        newowner1 = event['args']['depositor']
        amount1 = event['args']['amount']
