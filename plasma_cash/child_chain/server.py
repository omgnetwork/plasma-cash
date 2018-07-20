import json

from flask import Blueprint, request

from plasma_cash.child_chain import websocket, on
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
    if 'wsgi.websocket' in request.environ:
        return websocket.listen(request)
    else:
        return ''


@websocket.on('join')
def join(ws, arg):
    clients[arg] = ws


@websocket.on('left')
def left(ws, arg):
    del clients[arg]


@websocket.on('relay')
def relay(ws, arg):
    dest = clients[arg['dest']]
    msg = arg['message']
    dest.send(json.dumps({'event': 'relay', 'arg': msg}))


@on('block')
def on_block(block_number):
    for ws in clients.values():
        ws.send(json.dumps({'event': 'block', 'arg': block_number}))
