from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.client.child_chain_client import ChildChainClient
from plasma_cash.client.client import Client
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer


class DependencyContainer(object):
    def __init__(self):
        self._root_chain = None
        self._child_chain = None
        self._child_chain_client = None
        self._client = None

    def get_root_chain(self):
        if self._root_chain is None:
            self._root_chain = Deployer().get_contract('RootChain/RootChain.sol')
        return self._root_chain

    def get_child_chain(self):
        if self._child_chain is None:
            authority = plasma_config['AUTHORITY']
            root_chain = self.get_root_chain()
            self._child_chain = ChildChain(authority, root_chain)
        return self._child_chain

    def get_child_chain_client(self):
        if self._child_chain_client is None:
            self._child_chain_client = ChildChainClient('http://localhost:8546')
        return self._child_chain_client

    def get_client(self):
        if self._client is None:
            root_chain = self.get_root_chain()
            child_chain = self.get_child_chain_client()
            self._client = Client(root_chain, child_chain)
        return self._client


container = DependencyContainer()
