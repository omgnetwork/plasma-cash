import json

from flask import Blueprint, request
from geventwebsocket.exceptions import WebSocketError

from plasma_cash.dependency_config import container

bp = Blueprint('api', __name__)
ws = Blueprint('ws', __name__)

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


@ws.route('/')
def websocket(socket):
    global clients
    try:
        while True:
            data = json.loads(socket.receive())

            if data['event'] == 'join':
                clients[data['arg']] = socket
            elif data['event'] == 'left':
                del clients[data['arg']]
            elif data['event'] == 'relay':
                dest = clients[data['arg']['dest']]
                msg = data['arg']['message']
                dest.send(json.dumps({'event': 'relay', 'arg': msg}))
    except (WebSocketError, TypeError) as e:
        clients = {addr: sock for addr, sock in clients.items() if sock is not socket}
