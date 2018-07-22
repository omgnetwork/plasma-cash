import json

from flask import Blueprint, request

from plasma_cash.child_chain import websocket, event
from plasma_cash.dependency_config import container

bp = Blueprint('api', __name__)
clients = {}


@bp.route('/block', methods=['GET'])
def get_current_block():
    return container.get_child_chain().get_current_block()


@bp.route('/block/<blknum>', methods=['GET'])
def get_block(blknum):
    return container.get_child_chain().get_block(int(blknum))


@bp.route('/proof', methods=['GET'])
def get_proof():
    blknum = int(request.args.get('blknum'))
    uid = int(request.args.get('uid'))
    return container.get_child_chain().get_proof(blknum, uid)


@bp.route('/submit_block', methods=['POST'])
def submit_block():
    sig = request.form['sig']
    return container.get_child_chain().submit_block(sig)


@bp.route('/send_tx', methods=['POST'])
def send_tx():
    tx = request.form['tx']
    return container.get_child_chain().apply_transaction(tx)


@bp.route('/', methods=['GET'])
def root():
    global clients

    if 'wsgi.websocket' in request.environ:
        ws = websocket.listen(request)

        # Handle WebSocket disconnection, remove socket from client list
        clients = {k: v for k, v in clients.items() if v is not ws}

    # Path / is not an API entry
    return ''


@event.on('websocket.join')
def join(ws, arg):
    clients[arg] = ws


@event.on('websocket.left')
def left(ws, arg):
    del clients[arg]


@event.on('websocket.relay')
def relay(ws, arg):
    dest = clients[arg['dest']]
    msg = arg['message']
    dest.send(json.dumps({'event': 'relay', 'arg': msg}))


@event.on('chain.block')
def on_block(block_number):
    for ws in clients.values():
        ws.send(json.dumps({'event': 'block', 'arg': block_number}))
