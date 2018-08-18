import rlp
from ethereum import utils
from rlp.sedes import CountableList

from plasma_cash.utils.merkle.sparse_merkle_tree import SparseMerkleTree

from .transaction import Transaction


class Block(rlp.Serializable):

    fields = [
        ('transaction_set', CountableList(Transaction)),
    ]

    def __init__(self, transaction_set=None):
        if transaction_set is None:
            transaction_set = []

        self.transaction_set = transaction_set
        self.merkle = None

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self))

    def merklize_transaction_set(self):
        hashed_transaction_dict = {tx.uid: tx.merkle_hash for tx in self.transaction_set}
        self.merkle = SparseMerkleTree(257, hashed_transaction_dict)
        return self.merkle.root

    def add_tx(self, tx):
        self.transaction_set.append(tx)

    def get_tx_by_uid(self, uid):
        for tx in self.transaction_set:
            if tx.uid == uid:
                return tx
        return None
