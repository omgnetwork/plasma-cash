from flask import Flask
from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer


app = Flask(__name__)
child_chain = ChildChain(plasma_config['AUTHORITY'], Deployer().get_contract("RootChain/RootChain.sol"))
