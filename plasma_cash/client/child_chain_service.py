import requests


class ChildChainService(object):

    def __init__(self, base_url, verify=False, timeout=5):
        self.base_url = base_url
        self.verify = verify
        self.timeout = timeout

    def request(self, end_point, method, params=None, data=None, headers=None):
        url = self.base_url + end_point
        try:
            response = requests.request(
                           method=method,
                           url=url,
                           params=params,
                           data=data,
                           headers=headers,
                           verify=self.verify,
                           timeout=self.timeout,
                       )
        except requests.exceptions.Timeout:
            raise Exception
        except requests.exceptions.ConnectionError:
            raise Exception

        if response.ok:
            return response
        else:
            raise Exception
