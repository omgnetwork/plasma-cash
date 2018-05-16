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

    def test_submit_block(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        SIG = 'sig'
        DUMMY_MERKLE_HASH = 'merkle hash'
        when(self.CHILD_CHAIN).submit_block(SIG).thenReturn(DUMMY_MERKLE_HASH)

        resp = client.post('submit_block', data={'sig': SIG})
        assert resp.data == DUMMY_MERKLE_HASH.encode()

    def test_send_tx(self, client):
        (when('plasma_cash.child_chain.server.container')
            .get_child_chain().thenReturn(self.CHILD_CHAIN))

        DUMMY_TX = 'tx'
        DUMMY_TX_HASH = 'tx hash'
        when(self.CHILD_CHAIN).apply_transaction(DUMMY_TX).thenReturn(DUMMY_TX_HASH)

        resp = client.post('send_tx', data={'tx': DUMMY_TX})
        assert resp.data == DUMMY_TX_HASH.encode()
