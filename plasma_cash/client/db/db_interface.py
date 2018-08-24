import abc


class DbInterface(abc.ABC):

    @abc.abstractmethod
    def get_history(self, uid):
        return NotImplemented

    @abc.abstractmethod
    def save_history(self, uid, history):
        return NotImplemented
