class RequestFailedException(Exception):
    """request failed without success http status"""


class TxHistoryNotFoundException(Exception):
    """tx history is not found for specific block number"""
