import abc


class JobInterface(abc.ABC):

    @abc.abstractmethod
    def run(self):
        return NotImplemented
