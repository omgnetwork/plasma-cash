from plasma_cash.root_chain.deployer import Deployer
from .child_chain_service import ChildChainService


class Client(object):

    def __init__(self,
                 root_chain=Deployer().get_contract('RootChain/RootChain.sol'),
                 child_chain=ChildChainService('http://localhost:8546')):
        self.root_chain = root_chain
        self.child_chain = child_chain
