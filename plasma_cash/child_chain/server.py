from flask import Blueprint, request

from plasma_cash.dependency_config import container

bp = Blueprint('api', __name__)


@bp.route('/block', methods=['GET'])
def get_current_block():
    return container.get_child_chain().get_current_block()


@bp.route('/block/<blknum>', methods=['GET'])
def get_block(blknum):
    return container.get_child_chain().get_block(blknum)


@bp.route('/proof', methods=['GET'])
def get_tx_proof():
    blknum = request.args.get('blknum')
    uid = request.args.get('uid')
    return container.get_child_chain().get_tx_proof(blknum, uid)


@bp.route('/submit_block', methods=['POST'])
def submit_block():
    sig = request.form['sig']
    return container.get_child_chain().submit_block(sig)


@bp.route('/send_tx', methods=['POST'])
def send_tx():
    tx = request.form['tx']
    return container.get_child_chain().apply_transaction(tx)
