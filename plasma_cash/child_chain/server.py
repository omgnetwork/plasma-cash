from flask import Flask, request

from plasma_cash.child_chain.child_chain import ChildChain
from plasma_cash.config import plasma_config
from plasma_cash.root_chain.deployer import Deployer

app = Flask(__name__)


def get_child_chain():
    authority = plasma_config['AUTHORITY']
    root_chain = Deployer().get_contract('RootChain/RootChain.sol')
    return ChildChain(authority, root_chain)


@app.route('/block', methods=['GET'])
def get_current_block():
    return get_child_chain().get_current_block()


@app.route('/submit_block', methods=['POST'])
def submit_block():
    sig = request.form['sig']
    return get_child_chain().submit_block(sig)


@app.route('/send_tx', methods=['POST'])
def send_tx():
    tx = request.form['tx']
    return get_child_chain().apply_transaction(tx)
