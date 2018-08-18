import json
import threading

import requests
import websocket

from .exceptions import RequestFailedException


class ChildChainClient(object):

    def __init__(self, base_url, ws_url, verify=False, timeout=5):
        self.base_url = base_url
        self.verify = verify
        self.timeout = timeout

        self.ws = websocket.WebSocketApp(ws_url, on_message=self.ws_on_message)
        self.ws_callback = {}
        threading.Thread(target=self.ws.run_forever).start()

    def ws_on_message(self, ws, message):
        data = json.loads(message)
        if callable(self.ws_callback[data['event']]):
            self.ws_callback[data['event']](data['arg'])

    def emit(self, event, arg):
        self.ws.send(json.dumps({'event': event, 'arg': arg}, sort_keys=True))

    def on(self, event, callback):
        self.ws_callback[event] = callback

    def request(self, end_point, method, params=None, data=None, headers=None):
        url = self.base_url + end_point

        response = requests.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            verify=self.verify,
            timeout=self.timeout,
        )

        if response.ok:
            return response
        else:
            raise RequestFailedException(
                'failed reason: {}, text: {}'.format(response.reason, response.text)
            )

    def get_current_block(self):
        end_point = '/block'
        response = self.request(end_point, 'GET')
        return response.text

    def get_block(self, blknum):
        end_point = '/block/{}'.format(blknum)
        response = self.request(end_point, 'GET')
        return response.text

    def get_proof(self, blknum, uid):
        end_point = '/proof'
        params = {'blknum': blknum, 'uid': uid}
        response = self.request(end_point, 'GET', params=params)
        return response.text

    def send_transaction(self, tx):
        end_point = '/send_tx'
        data = {'tx': tx}
        self.request(end_point, 'POST', data=data)

    def submit_block(self, sig):
        end_point = '/operator/submit_block'
        data = {'sig': sig}
        self.request(end_point, 'POST', data=data)

    def apply_deposit(self, depositor, amount, uid):
        end_point = '/operator/apply_deposit'
        data = {'depositor': depositor, 'amount': amount, 'uid': uid}
        self.request(end_point, 'POST', data=data)
