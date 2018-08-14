from .db_interface import DbInterface


class MemoryDb(DbInterface):

    def __init__(self):
        self.uid = {}

    def get_history(self, uid):
        return self.uid.get(uid)

    def save_history(self, uid, history):
        self.uid[uid] = history
