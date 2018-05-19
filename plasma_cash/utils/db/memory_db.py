from .db_interface import DbInterface
from .exceptions import BlockAlreadyExistsException


class MemoryDb(DbInterface):

    def __init__(self):
        self.blocks = {}

    def get_block(self, block_number):
        return self.blocks.get(block_number)

    def save_block(self, block, block_number):
        if block_number in self.blocks:
            raise BlockAlreadyExistsException('should not save block with same id again.')
        self.blocks[block_number] = block
