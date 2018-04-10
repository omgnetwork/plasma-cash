import rlp
from rlp.sedes import binary, CountableList
from ethereum import utils
from plasma_cash.utils.merkle.sparse_merkle_tree import SparseMerkleTree
from plasma_cash.utils.utils import sign, get_sender
from .transaction import Transaction


class Block(rlp.Serializable):

    fields = [
        ('transaction_set', CountableList(Transaction)),
        ('sig', binary),
    ]

    def __init__(self, transaction_set=[], sig=b'\x00' * 65):
        self.transaction_set = transaction_set
        self.sig = sig
        self.merkle = None

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self, UnsignedBlock))

    @property
    def merkilize_transaction_set(self):
        hashed_transaction_dict = {tx.uid: tx.merkle_hash for tx in self.transaction_set}
        self.merkle = SparseMerkleTree(hashed_transaction_dict)
        return self.merkle.root

    @property
    def sender(self):
        return get_sender(self.hash, self.sig)

    def sign(self, key):
        self.sig = sign(self.hash, key)


UnsignedBlock = Block.exclude(['sig'])
