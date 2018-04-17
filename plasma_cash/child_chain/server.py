from flask import Flask, request

from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer

authority = plasma_config['AUTHORITY']
root_chain = Deployer().get_contract('RootChain/RootChain.sol')
child_chain = ChildChain(authority, root_chain)

app = Flask(__name__)


@app.route('/block', methods=['GET'])
def get_current_block():
    return child_chain.get_current_block()


@app.route('/submit_block', methods=['POST'])
def submit_block():
    sig = request.form['sig']
    return child_chain.submit_block(sig)
