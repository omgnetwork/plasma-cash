import pytest

from plasma_cash.client.exceptions import TxHistoryNotFoundException
from plasma_cash.client.history import History


class TestHistory(object):
    DUMMY_DEPOSIT_BLK_NUM = 1
    DUMMY_TX1 = 'dummy tx1'
    DUMMY_PROOF1 = 'dummy proof1'

    @pytest.fixture(scope='function')
    def history(self):
        return History(self.DUMMY_DEPOSIT_BLK_NUM, self.DUMMY_TX1, self.DUMMY_PROOF1)

    def test_constructor(self):
        history = History(self.DUMMY_DEPOSIT_BLK_NUM, self.DUMMY_TX1, self.DUMMY_PROOF1)
        assert history.latest_tx_blk_num == self.DUMMY_DEPOSIT_BLK_NUM
        assert history.tx_history == [self.DUMMY_TX1]
        assert history.proofs == [self.DUMMY_PROOF1]
        assert history.blk_num == [self.DUMMY_DEPOSIT_BLK_NUM]

    def test_update_history(self, history):
        DUMMY_BLK_NUM = 2
        DUMMY_TX2 = 'dummy tx2'
        DUMMY_PROOF2 = 'dummy proof2'
        history.update_tx_history(DUMMY_BLK_NUM, DUMMY_TX2, DUMMY_PROOF2)
        assert history.latest_tx_blk_num == 2
        assert history.tx_history == [self.DUMMY_TX1, DUMMY_TX2]
        assert history.proofs == [self.DUMMY_PROOF1, DUMMY_PROOF2]
        assert history.blk_num == [1, 2]

    def test_update_empty_history(self, history):
        DUMMY_BLK_NUM = 2
        EMPTY_TX = b'\x00' * 32
        NON_INCLUSIVE_PROOF = 'non inclusion proof'
        history.update_tx_history(DUMMY_BLK_NUM, EMPTY_TX, NON_INCLUSIVE_PROOF)
        assert history.latest_tx_blk_num == 1
        assert history.tx_history == [self.DUMMY_TX1, EMPTY_TX]
        assert history.proofs == [self.DUMMY_PROOF1, NON_INCLUSIVE_PROOF]
        assert history.blk_num == [1, 2]

    def test_update_history_with_wrong_order(self, history):
        DUMMY_BLK_NUM = 3
        DUMMY_TX3 = 'dummy tx3'
        DUMMY_PROOF3 = 'dummy proof3'
        history.update_tx_history(DUMMY_BLK_NUM, DUMMY_TX3, DUMMY_PROOF3)
        assert history.tx_history == [self.DUMMY_TX1, DUMMY_TX3]
        assert history.proofs == [self.DUMMY_PROOF1, DUMMY_PROOF3]
        assert history.blk_num == [1, 3]

        DUMMY_BLK_NUM = 2
        DUMMY_TX2 = 'dummy tx2'
        DUMMY_PROOF2 = 'dummy proof2'
        history.update_tx_history(DUMMY_BLK_NUM, DUMMY_TX2, DUMMY_PROOF2)
        assert history.tx_history == [self.DUMMY_TX1, DUMMY_TX3, DUMMY_TX2]
        assert history.proofs == [self.DUMMY_PROOF1, DUMMY_PROOF3, DUMMY_PROOF2]
        assert history.blk_num == [1, 3, 2]

    def test_get_data_by_block(self, history):
        DUMMY_BLK_NUM = 1
        tx, proof = history.get_data_by_block(DUMMY_BLK_NUM)
        assert tx == history.tx_history[0]
        assert proof == history.proofs[0]

    def test_get_data_by_block_failed(self, history):
        DUMMY_BLK_NUM = 2
        with pytest.raises(TxHistoryNotFoundException):
            history.get_data_by_block(DUMMY_BLK_NUM)
