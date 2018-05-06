from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer


class DependencyContainer(object):
    def __init__(self):
        self._child_chain = None

    def get_child_chain(self):
        if self._child_chain is None:
            authority = plasma_config['AUTHORITY']
            root_chain = Deployer().get_contract('RootChain/RootChain.sol')
            self._child_chain = ChildChain(authority, root_chain)
        return self._child_chain


container = DependencyContainer()
