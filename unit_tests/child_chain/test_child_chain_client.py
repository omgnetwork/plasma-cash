import pytest
from mockito import mock, verify, when

from plasma_cash.child_chain.child_chain_client import ChildChainClient
from plasma_cash.child_chain.exceptions import RequestFailedException
from unit_tests.unstub_mixin import UnstubMixin


class TestChildChainClient(UnstubMixin):
    BASE_URL = 'https://dummy-plasma-cash'
    WS_URL = 'ws://dummy-plasma-cash'

    @pytest.fixture(scope='function')
    def client(self):
        return ChildChainClient(self.BASE_URL, self.WS_URL)

    def test_constructor(self):
        DUMMY_BASE_URL = 'base url'
        DUMMY_WS_URL = 'ws url'
        DUMMY_VERIFY = True
        DUMMY_TIME_OUT = 100

        c = ChildChainClient(DUMMY_BASE_URL, DUMMY_WS_URL, DUMMY_VERIFY, DUMMY_TIME_OUT)
        assert c.base_url == DUMMY_BASE_URL
        assert c.verify == DUMMY_VERIFY
        assert c.timeout == DUMMY_TIME_OUT

    def test_ws_on_message(self, client):
        DUMMY_WS = 'ws'
        DUMMY_EVENT = 'event'
        DUMMY_ARG = 'arg'
        DUMMY_MESSAGE = '{"arg": "arg", "event": "event"}'

        handler = mock()
        when(handler).__call__(DUMMY_ARG).thenReturn(DUMMY_ARG)
        client.ws_callback[DUMMY_EVENT] = handler
        client.ws_on_message(DUMMY_WS, DUMMY_MESSAGE)
        verify(handler).__call__(DUMMY_ARG)

    def test_emit(self, client):
        DUMMY_EVENT = 'event'
        DUMMY_ARG = 'arg'
        DUMMY_MESSAGE = '{"arg": "arg", "event": "event"}'

        when(client.ws).send(any).thenReturn(None)
        client.emit(DUMMY_EVENT, DUMMY_ARG)
        verify(client.ws).send(DUMMY_MESSAGE)

    def test_on(self, client):
        DUMMY_EVENT = 'event'
        DUMMY_HANDLER = 'handler'

        client.on(DUMMY_EVENT, DUMMY_HANDLER)
        assert client.ws_callback[DUMMY_EVENT] == DUMMY_HANDLER

    def test_request_success(self, client):
        DUMMY_END_POINT = '/end-point'
        DUMMY_METHOD = 'post'
        DUMMY_PARAMS = 'parmas'
        DUMMY_DATA = {'data': 'dummy'}
        DUMMY_HEADERS = 'headers'

        URL = self.BASE_URL + DUMMY_END_POINT

        MOCK_RESPONSE = mock({'ok': True})

        (when('plasma_cash.child_chain.child_chain_client.requests')
            .request(
                method=DUMMY_METHOD,
                url=URL,
                params=DUMMY_PARAMS,
                data=DUMMY_DATA,
                headers=DUMMY_HEADERS,
                verify=client.verify,
                timeout=client.timeout
            ).thenReturn(MOCK_RESPONSE))

        resp = client.request(
            DUMMY_END_POINT,
            DUMMY_METHOD,
            DUMMY_PARAMS,
            DUMMY_DATA,
            DUMMY_HEADERS
        )

        assert resp == MOCK_RESPONSE

    def test_request_failed(self, client):
        DUMMY_END_POINT = '/end-point'
        DUMMY_METHOD = 'post'
        DUMMY_PARAMS = 'parmas'
        DUMMY_DATA = {'data': 'dummy'}
        DUMMY_HEADERS = 'headers'

        URL = self.BASE_URL + DUMMY_END_POINT

        MOCK_RESPONSE = mock({'ok': False})

        (when('plasma_cash.child_chain.child_chain_client.requests')
            .request(
                method=DUMMY_METHOD,
                url=URL,
                params=DUMMY_PARAMS,
                data=DUMMY_DATA,
                headers=DUMMY_HEADERS,
                verify=client.verify,
                timeout=client.timeout
            ).thenReturn(MOCK_RESPONSE))

        with pytest.raises(RequestFailedException):
            client.request(
                DUMMY_END_POINT,
                DUMMY_METHOD,
                DUMMY_PARAMS,
                DUMMY_DATA,
                DUMMY_HEADERS
            )

    def test_get_current_block(self, client):
        RESP_TEXT = 'response text'
        MOCK_RESP = mock({'text': RESP_TEXT})

        when(client).request('/block', 'GET').thenReturn(MOCK_RESP)
        resp = client.get_current_block()
        assert resp == RESP_TEXT

    def test_get_block(self, client):
        RESP_TEXT = 'response text'
        MOCK_RESP = mock({'text': RESP_TEXT})
        DUMMY_BLK_NUM = 1

        when(client).request('/block/{}'.format(DUMMY_BLK_NUM), 'GET').thenReturn(MOCK_RESP)
        resp = client.get_block(DUMMY_BLK_NUM)
        assert resp == RESP_TEXT

    def test_get_proof(self, client):
        RESP_TEXT = 'response text'
        MOCK_RESP = mock({'text': RESP_TEXT})
        DUMMY_BLK_NUM = 1
        DUMMY_UID = 1

        params = {'blknum': DUMMY_BLK_NUM, 'uid': DUMMY_UID}
        when(client).request('/proof', 'GET', params=params).thenReturn(MOCK_RESP)
        resp = client.get_proof(DUMMY_BLK_NUM, DUMMY_UID)
        assert resp == RESP_TEXT

    def test_send_transaction(self, client):
        DUMMY_TX = 'tx'
        when(client).request(any, any, data=any).thenReturn(None)
        client.send_transaction(DUMMY_TX)
        verify(client).request(
            '/send_tx',
            'POST',
            data={'tx': DUMMY_TX}
        )

    def test_submit_block(self, client):
        DUMMY_SIG = 'sig'
        when(client).request(any, any, data=any).thenReturn(None)
        client.submit_block(DUMMY_SIG)
        verify(client).request(
            '/operator/submit_block',
            'POST',
            data={'sig': DUMMY_SIG}
        )

    def test_apply_deposit(self, client):
        DUMMY_DEPOSITOR = 'depositor'
        DUMMY_AMOUNT = 123
        DUMMY_UID = 0

        when(client).request(any, any, data=any).thenReturn(None)
        client.apply_deposit(DUMMY_DEPOSITOR, DUMMY_AMOUNT, DUMMY_UID)

        request_data = {
            'depositor': DUMMY_DEPOSITOR,
            'amount': DUMMY_AMOUNT,
            'uid': DUMMY_UID
        }
        verify(client).request(
            '/operator/apply_deposit',
            'POST',
            data=request_data
        )
