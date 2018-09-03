import os

from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.child_chain.child_chain_client import ChildChainClient
from plasma_cash.child_chain.db.leveldb import LevelDb
from plasma_cash.child_chain.db.memory_db import MemoryDb
from plasma_cash.config import PROJECT_DIR, db_config, plasma_config
from plasma_cash.root_chain.deployer import Deployer


class DependencyContainer(object):
    def __init__(self):
        self._root_chain = None
        self._child_chain = None
        self._child_chain_client = None
        self._db = None

    def get_db(self):
        if self._db is None:
            db_type = db_config['type']
            if db_type == 'memory':
                self._db = MemoryDb()
            elif db_type == 'leveldb':
                if db_config.get('path'):
                    path = db_config['path']
                else:
                    path = os.path.join(PROJECT_DIR, '.db')
                self._db = LevelDb(path)
            else:
                raise ValueError('type of {} is not supported'.format(db_type))

        return self._db

    def get_root_chain(self):
        if self._root_chain is None:
            self._root_chain = Deployer().get_contract('RootChain/RootChain.sol')
        return self._root_chain

    def get_child_chain(self):
        if self._child_chain is None:
            key = plasma_config['AUTHORITY_KEY']
            root_chain = self.get_root_chain()
            db = self.get_db()
            self._child_chain = ChildChain(key, root_chain, db)
        return self._child_chain

    def get_child_chain_client(self):
        if self._child_chain_client is None:
            self._child_chain_client = ChildChainClient(
                'http://localhost:8546',
                'ws://localhost:8546'
            )
        return self._child_chain_client


container = DependencyContainer()
