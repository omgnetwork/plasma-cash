class InvalidTxSignatureException(Exception):
    """the signature of a tx is invalid"""


class InvalidBlockSignatureException(Exception):
    """the signature of a block is invalid"""


class PreviousTxNotFoundException(Exception):
    """previous transaction is not found"""


class TxAlreadySpentException(Exception):
    """the transaction is already spent"""


class TxAmountMismatchException(Exception):
    """tx input total amount is not equal to output total amount"""


class InvalidBlockNumException(Exception):
    """block num does not have related block"""


class TxWithSameUidAlreadyExists(Exception):
    """the block already has one tx with the uid"""


class RequestFailedException(Exception):
    """request failed without success http status"""


class DepositAlreadyAppliedException(Exception):
    """the deposit is already applied"""
