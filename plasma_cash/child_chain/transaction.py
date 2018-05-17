import rlp
from ethereum import utils
from rlp.sedes import big_endian_int, binary

from plasma_cash.utils.utils import get_sender, sign


class Transaction(rlp.Serializable):

    fields = [
        ('prev_block', big_endian_int),
        ('uid', big_endian_int),
        ('amount', big_endian_int),
        ('new_owner', utils.address),
        ('sig', binary)
    ]

    def __init__(self, prev_block, uid, amount, new_owner, sig=b'\x00' * 65):
        self.prev_block = prev_block
        self.uid = uid
        self.amount = amount
        self.new_owner = new_owner
        self.sig = sig

        self.spent = False

    @property
    def hash(self):
        return utils.sha3(rlp.encode(self, UnsignedTransaction))

    @property
    def merkle_hash(self):
        return utils.sha3(rlp.encode(self))

    @property
    def sender(self):
        return get_sender(self.hash, self.sig)

    def sign(self, key):
        self.sig = sign(self.hash, key)


UnsignedTransaction = Transaction.exclude(['sig'])
