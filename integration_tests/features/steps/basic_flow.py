import time

from behave import given, then, when
from web3.auto import w3

from integration_tests.features.utils import address_equals, has_value
from plasma_cash.client.client import Client
from plasma_cash.dependency_config import container

userA = '0xb83e232458A092696bE9717045d9A605FB0FEc2b'
userB = '0x08d92dcA9038eA9433254996a2D4F08D43BE8227'
userA_key = '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b'
userB_key = '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30'
eth_currency = '0x0000000000000000000000000000000000000000'
operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
uid = 1693390459388381052156419331572168595237271043726428428352746834777341368960

DEPOSIT_TX_BLOCK = 1  # only one block is generated after deposit
TRANSFER_TX_BLOCK = 2


@given('userA and userB has {amount:d} eth in root chain')
def userA_has_some_amount_of_eth_in_root_chain(context, amount):
    userA_balance = w3.eth.getBalance(userA)
    assert_msg = 'userA balance in {} does not match expected amount: {} in eth'.format(
        w3.fromWei(userA_balance, 'ether'),
        amount
    )
    assert w3.toWei(amount, 'ether') == userA_balance, assert_msg

    userB_balance = w3.eth.getBalance(userB)
    assert_msg = 'userB balance in {} does not match expected amount: {} in eth'.format(
        w3.fromWei(userB_balance, 'ether'),
        amount
    )
    assert w3.toWei(amount, 'ether') == userB_balance, assert_msg


@when('userA deposit {amount:d} eth to plasma')
def userA_deposit_some_eth_to_plasma(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.deposit(amount=amount, currency=eth_currency)
    time.sleep(5)


@then('userA has around {amount:d} eth in root chain')
def userA_has_around_some_amount_of_eth_in_root_chain(context, amount):
    balance = w3.eth.getBalance(userA)
    assert_msg = 'balance: {} is not in around: {}'.format(w3.fromWei(balance, 'ether'), amount)
    assert w3.toWei(amount - 0.01, 'ether') <= balance <= w3.toWei(amount, 'ether'), assert_msg


@then('userA has {amount:d} eth in the deposit tx in plasma cash')
def userA_have_some_amount_of_eth_in_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    block = client.get_block(DEPOSIT_TX_BLOCK)
    tx = block.get_tx_by_uid(uid)
    assert tx.amount == amount, 'tx.amount {} != amount: {}'.format(tx.amount, amount)

    assert_msg = 'new_owner {} is not same address as userA: {}'.format(tx.new_owner.hex(), userA)
    assert address_equals(tx.new_owner.hex(), userA), assert_msg


@when('userA transfer {amount:d} eth to userB in child chain')
def userA_transfer_some_eth_to_userB_in_child_chain(context, amount):
    prev_block = DEPOSIT_TX_BLOCK
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.send_transaction(prev_block, uid, amount, userB)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@then('userB has {amount:d} eth in the transfer tx in plasma cash')
def userB_has_some_amount_of_eth_in_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
    block = client.get_block(TRANSFER_TX_BLOCK)
    tx = block.get_tx_by_uid(uid)
    assert tx.amount == amount, 'tx.amount {} != amount: {}'.format(tx.amount, amount)

    assert_msg = 'tx.new_owner {} not same address as userB: {}'.format(tx.new_owner.hex(), userB)
    assert address_equals(tx.new_owner.hex(), userB), assert_msg


@when('userB start exit {amount:d} eth from plasma cash')
def userB_start_exit_some_eth_from_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
    client.start_exit(uid, prev_tx_blk_num=1, tx_blk_num=2)
    time.sleep(5)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@then('root chain got userB start exit {amount:d} eth')
def root_chain_got_userB_start_exit(context, amount):
    root_chain = container.get_root_chain()
    assert has_value(root_chain.functions.exits(uid).call())


@when('two weeks have passed')
def two_week_passed(context):
    TWO_WEEK_SECOND = 60 * 60 * 24 * 14
    for provider in w3.providers:
        provider.make_request('evm_increaseTime', TWO_WEEK_SECOND)


@when('userB finalize the exit')
def userB_finalize_exit(context):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
    client.finalize_exit(uid)
    time.sleep(5)


@then('userB has around {amount:d} eth in root chain after exit')
def userB_successfully_exit_from_root_chain_after_exit(context, amount):
    balance = w3.eth.getBalance(userB)
    assert_msg = 'balance: {} is not in around: {}'.format(w3.fromWei(balance, 'ether'), amount)
    assert w3.toWei(amount - 0.05, 'ether') <= balance <= w3.toWei(amount, 'ether'), assert_msg
