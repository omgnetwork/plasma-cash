import pytest
from mockito import ANY, when

from plasma_cash.child_chain.block import Block
from plasma_cash.child_chain.db.exceptions import BlockAlreadyExistsException
from plasma_cash.child_chain.db.leveldb import LevelDb
from unit_tests.unstub_mixin import UnstubMixin


def is_byte(data):
    try:
        data = data.decode()
    except Exception:
        return False
    return True


class FakeLevelDb(object):
    def __init__(self):
        self.data = {}

    def put(self, k, v):
        if not is_byte(k) or not is_byte(v):
            raise Exception('leveldb could only take byte type as input')
        self.data[k] = v

    def get(self, k):
        if not is_byte(k):
            raise Exception('leveldb could only take byte type as input')
        return self.data.get(k)


class TestLevelDb(UnstubMixin):

    @pytest.fixture(scope='function')
    def db(self):
        db = FakeLevelDb()
        (when('plasma_cash.child_chain.db.leveldb.plyvel')
            .DB(ANY, create_if_missing=True).thenReturn(db))
        return LevelDb('test_db')

    def test_block_normal_case(self, db):
        DUMMY_BLOCK = Block()
        DUMMY_BLK_NUM = 1
        db.save_block(DUMMY_BLOCK, DUMMY_BLK_NUM)
        assert db.get_block(DUMMY_BLK_NUM) == DUMMY_BLOCK

    def test_get_block_none(self, db):
        NON_EXIST_BLK_NUM = -1
        assert db.get_block(NON_EXIST_BLK_NUM) is None

    def test_save_block_already_exists(self, db):
        DUMMY_BLOCK = Block()
        DUMMY_BLK_NUM = 1
        db.save_block(DUMMY_BLOCK, DUMMY_BLK_NUM)
        with pytest.raises(BlockAlreadyExistsException):
            db.save_block('second block should fail', DUMMY_BLK_NUM)

    def test_get_current_block_num_first_time_return_1(self, db):
        assert db.get_current_block_num() == 1

    def test_increment_current_block_num(self, db):
        block_num = db.get_current_block_num()
        db.increment_current_block_num()
        block_num_incr = db.get_current_block_num()
        assert block_num_incr == block_num + 1
