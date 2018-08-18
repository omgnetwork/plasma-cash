import pytest
from mockito import mock, when

from plasma_cash.child_chain import create_app
from unit_tests.unstub_mixin import UnstubMixin


class TestServer(UnstubMixin):
    CHILD_CHAIN = mock()

    @pytest.fixture(scope='function')
    def app(self):
        app = create_app(is_unit_test=True)
        app.config['TESTING'] = True
        return app

    @pytest.fixture(scope='function')
    def client(self, app):
        return app.test_client()

    def test_get_current_block(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        DUMMY_BLOCK = 'block'
        when(self.CHILD_CHAIN).get_current_block().thenReturn(DUMMY_BLOCK)

        resp = client.get('block')
        assert resp.data == DUMMY_BLOCK.encode()

    def test_get_block(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        DUMMY_BLK_NUM = 1
        DUMMY_BLOCK = 'block'
        when(self.CHILD_CHAIN).get_block(DUMMY_BLK_NUM).thenReturn(DUMMY_BLOCK)

        resp = client.get('block/1')
        assert resp.data == DUMMY_BLOCK.encode()

    def test_get_proof(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        DUMMY_PROOF = 'proof'
        DUMMY_BLK_NUM = 1
        DUMMY_UID = 1
        when(self.CHILD_CHAIN).get_proof(DUMMY_BLK_NUM, DUMMY_UID).thenReturn(DUMMY_PROOF)

        resp = client.get('/proof', query_string={'blknum': 1, 'uid': 1})
        assert resp.data == DUMMY_PROOF.encode()

    def test_send_tx(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        DUMMY_TX = 'tx'
        DUMMY_TX_HASH = 'tx hash'
        when(self.CHILD_CHAIN).apply_transaction(DUMMY_TX).thenReturn(DUMMY_TX_HASH)

        resp = client.post('send_tx', data={'tx': DUMMY_TX})
        assert resp.data == DUMMY_TX_HASH.encode()

    def test_submit_block(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        SIG = 'sig'
        DUMMY_MERKLE_HASH = 'merkle hash'
        when(self.CHILD_CHAIN).submit_block(SIG).thenReturn(DUMMY_MERKLE_HASH)

        resp = client.post('/operator/submit_block', data={'sig': SIG})
        assert resp.data == DUMMY_MERKLE_HASH.encode()

    def test_apply_deposit(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        DUMMY_DEPOSITOR = 'depositor'
        DUMMY_AMOUNT = 123
        DUMMY_UID = 0

        data = {
            'depositor': DUMMY_DEPOSITOR,
            'amount': DUMMY_AMOUNT,
            'uid': DUMMY_UID
        }

        DUMMY_TX_HASH = 'dummy tx hash'
        (when(self.CHILD_CHAIN)
            .apply_deposit(DUMMY_DEPOSITOR, DUMMY_AMOUNT, DUMMY_UID)
            .thenReturn(DUMMY_TX_HASH))

        resp = client.post('/operator/apply_deposit', data=data)
        assert resp.data == DUMMY_TX_HASH.encode()
