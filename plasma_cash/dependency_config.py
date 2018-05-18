from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.client.child_chain_client import ChildChainClient
from plasma_cash.client.client import Client
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer
from plasma_cash.utils.db.memory_db import MemoryDb


class DependencyContainer(object):
    def __init__(self):
        self._root_chain = None
        self._child_chain = None
        self._child_chain_client = None
        self._client = None

    def get_db(self):
        # TODO: enable real_db type & memory_db chosen by config
        return MemoryDb()

    def get_root_chain(self):
        if self._root_chain is None:
            self._root_chain = Deployer().get_contract('RootChain/RootChain.sol')
        return self._root_chain

    def get_child_chain(self):
        if self._child_chain is None:
            authority = plasma_config['AUTHORITY']
            root_chain = self.get_root_chain()
            db = self.get_db()
            self._child_chain = ChildChain(authority, root_chain, db)
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
