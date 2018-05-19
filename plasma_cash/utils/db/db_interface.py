import abc


class DbInterface(abc.ABC):

    @abc.abstractmethod
    def get_block(self, block_number):
        return NotImplemented

    @abc.abstractmethod
    def save_block(self, block, block_number):
        return NotImplemented
