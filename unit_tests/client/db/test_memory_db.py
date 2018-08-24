import pytest

from plasma_cash.client.db.memory_db import MemoryDb


class TestMemoryDb(object):
    @pytest.fixture(scope='function')
    def db(self):
        return MemoryDb()

    def test_save_and_get_history(self, db):
        DUMMY_HISTORY = 'dummy history'
        DUMMY_UID = 1
        db.save_history(DUMMY_UID, DUMMY_HISTORY)
        assert db.get_history(DUMMY_UID) == DUMMY_HISTORY

    def test_history_not_found(self, db):
        DUMMY_UID = 1
        assert db.get_history(DUMMY_UID) is None
