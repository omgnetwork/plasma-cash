from web3.auto import w3


def address_equals(address1, address2):
    return w3.toChecksumAddress(address1) == w3.toChecksumAddress(address2)


def has_value(obj):
    if len(obj) > 0:
        return obj[0]
    return False
