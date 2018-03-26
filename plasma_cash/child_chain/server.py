from flask import Flask
from plasma_cash.child_chain.child_chain import ChildChain


child_chain = ChildChain()
app = Flask(__name__)
