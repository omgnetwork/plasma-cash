import time

from behave import given, then, when
from web3.auto import w3

from integration_tests.features.utils import has_value
from plasma_cash.client.client import Client
from plasma_cash.dependency_config import container

userA = '0xb83e232458A092696bE9717045d9A605FB0FEc2b'
operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
userA_key = '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b'
eth_currency = '0x0000000000000000000000000000000000000000'
uid = 1693390459388381052156419331572168595237271043726428428352746834777341368960

DEPOSIT_TX_BLOCK = 1
TRANSFER_TX_1_BLOCK = 2


@given('userA deposits {amount:d} eth in plasma cash')
def userA_deposits_some_amount_of_eth_in_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.deposit(amount=amount, currency=eth_currency)
    time.sleep(5)


@when('userA starts to exit {amount:d} eth from plasma cash')
def userA_starts_to_exit_deposit_from_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.start_deposit_exit(uid, tx_blk_num=DEPOSIT_TX_BLOCK)
    time.sleep(5)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@then('root chain got the start-deposit-exit record')
def root_chain_got_the_start_deposit_exit_record(context):
    root_chain = container.get_root_chain()
    assert has_value(root_chain.functions.exits(uid).call({'from': userA}))


@when('two weeks have passed from depositing exit')
def two_week_passed(context):
    TWO_WEEK_SECOND = 60 * 60 * 24 * 14
    for provider in w3.providers:
        provider.make_request('evm_increaseTime', TWO_WEEK_SECOND)


@when('userA finalize the deposit exit')
def userA_finalize_exit(context):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.finalize_exit(uid)
    time.sleep(5)


@then('userA has around {amount:d} eth in root chain after exit')
def userB_successfully_exit_from_root_chain_after_exit(context, amount):
    balance = w3.eth.getBalance(userA)
    assert_msg = 'balance: {} is not in around: {}'.format(w3.fromWei(balance, 'ether'), amount)
    assert w3.toWei(amount - 0.05, 'ether') <= balance <= w3.toWei(amount, 'ether'), assert_msg
