import time

import rlp
from behave import given, then, when

from integration_tests.features.utils import has_value
from plasma_cash.client.client import Client
from plasma_cash.dependency_config import container

userA = '0xb83e232458A092696bE9717045d9A605FB0FEc2b'
userB = '0x08d92dcA9038eA9433254996a2D4F08D43BE8227'
userC = '0xDF29cFbD5d793Fa5B22D5c730A8E8450740C6f8f'
userD = '0xc5016A1Dc1F2556FD237AbBa2681D221Edf31A20'
operator_key = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
userA_key = '0xe4807cf08191b310fe1821e6e5397727ee6bc694e92e25115eca40114e3a4e6b'
userB_key = '0xee092298d0c0db61969cc4466d57571cf3ca36ca62db94273d5c1513312aeb30'
userC_key = '0x8af3051eb765261b245d586a88700e606431b199f2cce4c825d2b1921086b35c'
userD_key = '0x4d4c362239f610305b1c05ef91928c893d9a631e08149b7d66286fcf3dfa8553'
eth_currency = '0x0000000000000000000000000000000000000000'
uid = 1693390459388381052156419331572168595237271043726428428352746834777341368960

DEPOSIT_TX_BLOCK = 1
TRANSFER_TX_1_BLOCK = 2
TRANSFER_TX_2_BLOCK = 3
TRANSFER_TX_3_BLOCK = 4


@given('userA deposits {amount:d} eth in plasma cash')
def userA_deposits_some_amount_of_eth_in_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.deposit(amount=amount, currency=eth_currency)
    time.sleep(5)


@given('userA transfers {amount:d} eth to userB')
def userA_transfers_some_eth_to_userB(context, amount):
    prev_block = DEPOSIT_TX_BLOCK
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userA_key)
    client.send_transaction(prev_block, uid, amount, userB)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@given('userB transfers {amount:d} eth to userC')
def userB_transfers_some_eth_to_userC(context, amount):
    prev_block = TRANSFER_TX_1_BLOCK
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
    client.send_transaction(prev_block, uid, amount, userC)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@given('userC transfers {amount:d} eth to userD')
def userC_transfers_some_eth_to_userD(context, amount):
    prev_block = TRANSFER_TX_2_BLOCK
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userC_key)
    client.send_transaction(prev_block, uid, amount, userD)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@when('userD starts to exit {amount:d} eth from plasma cash')
def userD_starts_to_exit_some_eth_from_plasma_cash(context, amount):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userD_key)
    client.start_exit(uid, prev_tx_blk_num=TRANSFER_TX_2_BLOCK, tx_blk_num=TRANSFER_TX_3_BLOCK)
    time.sleep(5)

    operator = Client(container.get_root_chain(), container.get_child_chain_client(), operator_key)
    operator.submit_block()


@then('root chain got the start-exit record from history challenge')
def root_chain_got_the_start_exit_record_from_history_challenge(context):
    root_chain = container.get_root_chain()
    assert has_value(root_chain.functions.exits(uid).call({'from': userD}))


@when('userB challenges the exit history with deposit tx')
def userC_challenges_the_spent_coin_exit(context):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
    client.challenge_exit(uid, tx_blk_num=DEPOSIT_TX_BLOCK)
    time.sleep(5)


@then('root chain got the challenge record')
def then_root_chain_got_the_challenge_record(context):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userB_key)
    deposit_block = client.get_block(DEPOSIT_TX_BLOCK)
    deposit_tx = deposit_block.get_tx_by_uid(uid)

    root_chain = container.get_root_chain()
    assert root_chain.functions.isChallengeExisted(
        uid, rlp.encode(deposit_tx)
    ).call({'from': userB})


@when('userD responds to the history challenge')
def userD_responds_to_the_history_challenge(context):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userD_key)
    deposit_block = client.get_block(DEPOSIT_TX_BLOCK)
    deposit_tx = deposit_block.get_tx_by_uid(uid)

    client.respond_challenge_exit(
        rlp.encode(deposit_tx),
        uid,
        tx_blk_num=TRANSFER_TX_1_BLOCK
    )
    time.sleep(5)


@then('root chain cancels the challenge')
def then_root_chain_cancels_the_challenge(context):
    client = Client(container.get_root_chain(), container.get_child_chain_client(), userD_key)
    deposit_block = client.get_block(DEPOSIT_TX_BLOCK)
    deposit_tx = deposit_block.get_tx_by_uid(uid)

    root_chain = container.get_root_chain()
    assert not root_chain.functions.isChallengeExisted(
        uid, rlp.encode(deposit_tx)
    ).call({'from': userD})
