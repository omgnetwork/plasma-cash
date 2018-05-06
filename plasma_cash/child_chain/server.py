from flask import Flask, request

from plasma_cash.dependency_config import container

app = Flask(__name__)


@app.route('/block', methods=['GET'])
def get_current_block():
    return container.get_child_chain().get_current_block()


@app.route('/submit_block', methods=['POST'])
def submit_block():
    sig = request.form['sig']
    return container.get_child_chain().submit_block(sig)


@app.route('/send_tx', methods=['POST'])
def send_tx():
    tx = request.form['tx']
    return container.get_child_chain().apply_transaction(tx)
