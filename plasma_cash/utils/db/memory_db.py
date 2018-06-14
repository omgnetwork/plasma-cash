from .db_interface import DbInterface
from .exceptions import BlockAlreadyExistsException


class MemoryDb(DbInterface):

    def __init__(self):
        self.blocks = {}
        self.block_num = 1

    def get_block(self, block_number):
        return self.blocks.get(block_number)

    def save_block(self, block, block_number):
        if block_number in self.blocks:
            raise BlockAlreadyExistsException('should not save block with same blknum again.')
        self.blocks[block_number] = block

    def get_current_block_num(self):
        return self.block_num

    def increment_current_block_num(self):
        self.block_num += 1
        return self.block_num
