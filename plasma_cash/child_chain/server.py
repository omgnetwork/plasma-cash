from flask import Flask, request
from plasma_cash.child_chain.child_chain import ChildChain


child_chain = ChildChain()
app = Flask(__name__)

@app.route('/block', methods=['GET'])
def get_current_block():
    return child_chain.get_current_block()

@app.route('/submit_block', methods=['POST'])
def submit_block():
    sig = request.form['sig']
    return child_chain.submit_block(sig)
