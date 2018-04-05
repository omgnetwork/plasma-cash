import rlp
from rlp.sedes import binary, CountableList
from ethereum import utils
from plasma_cash.utils.merkle.sparse_merkle_tree import SparseMerkleTree
from plasma_cash.utils.utils import sign
from plasma_cash.child_chain.transaction import Transaction


class Block(rlp.Serializable):

    fields = [
        ('transaction_set', CountableList(Transaction)),
        ('sig', binary),
    ]

    def __init__(self, transaction_set={}, sig=b'\x00' * 65):
        self.transaction_set = transaction_set
        self.sig = sig
        self.merkle = None

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self, UnsignedBlock))

    @property
    def merkilize_transaction_set(self):
        hashed_transaction_set = {index: tx.merkle_hash for index, tx in self.transaction_set.items()}
        self.merkle = SparseMerkleTree(hashed_transaction_set)
        return self.merkle.root

    def sign(self, key):
        self.sig = sign(self.hash, key)


UnsignedBlock = Block.exclude(['sig'])
