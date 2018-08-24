import plyvel
import rlp
from ethereum import utils

from plasma_cash.child_chain.block import Block

from .db_interface import DbInterface
from .exceptions import BlockAlreadyExistsException


class LevelDb(DbInterface):
    CURRENT_BLOCK_NUM_KEY = b'current_block_num'

    def __init__(self, path):
        self.db = plyvel.DB(path, create_if_missing=True)

    def get_block(self, block_number):
        key = str.encode(str(block_number))
        encoded_block = self.db.get(key)
        if encoded_block:
            return rlp.decode(utils.decode_hex(encoded_block.decode()), Block)
        else:
            return None

    def save_block(self, block, block_number):
        key = str.encode(str(block_number))
        if self.db.get(key):
            raise BlockAlreadyExistsException('should not save block with same blknum again.')
        self.db.put(key, str.encode(rlp.encode(block).hex()))

    def get_current_block_num(self):
        current_block_num = self.db.get(self.CURRENT_BLOCK_NUM_KEY)
        if not current_block_num:
            self.db.put(self.CURRENT_BLOCK_NUM_KEY, '1'.encode())
            return 1
        return int(current_block_num.decode())

    def increment_current_block_num(self):
        current_block_num = self.get_current_block_num()
        incr_block_num = current_block_num + 1
        self.db.put(self.CURRENT_BLOCK_NUM_KEY, str(incr_block_num).encode())
        return incr_block_num
