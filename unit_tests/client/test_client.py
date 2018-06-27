import pytest
from mockito import ANY, mock, verify, when
from web3.auto import w3

from plasma_cash.child_chain.block import Block
from plasma_cash.client.client import Client
from unit_tests.unstub_mixin import UnstubMixin


class TestClient(UnstubMixin):

    @pytest.fixture(scope='function')
    def root_chain(self):
        root_chain = mock()
        root_chain.functions = mock()
        return root_chain

    @pytest.fixture(scope='function')
    def child_chain(self):
        return mock()

    @pytest.fixture(scope='function')
    def client(self, root_chain, child_chain):
        return Client(root_chain, child_chain)

    def test_constructor(self):
        DUMMY_ROOT_CHAIN = 'root chain'
        DUMMY_CHILD_CHAIN = 'child chain'
        c = Client(DUMMY_ROOT_CHAIN, DUMMY_CHILD_CHAIN)
        assert c.root_chain == DUMMY_ROOT_CHAIN
        assert c.child_chain == DUMMY_CHILD_CHAIN

    def test_deposit(self, client, root_chain):
        MOCK_TRANSACT = mock()
        DUMMY_AMOUNT = 1
        DUMMY_DEPOSITOR = 'dummy depositor'
        DUMMY_CURRENCY = 'dummy currency'

        when(w3).toChecksumAddress(DUMMY_DEPOSITOR).thenReturn(DUMMY_DEPOSITOR)
        when(root_chain.functions).deposit(DUMMY_CURRENCY, DUMMY_AMOUNT).thenReturn(MOCK_TRANSACT)

        client.deposit(DUMMY_AMOUNT, DUMMY_DEPOSITOR, DUMMY_CURRENCY)

        verify(MOCK_TRANSACT).transact(ANY)

    def test_submit_block(self, client, child_chain):
        MOCK_HASH = 'mock hash'
        MOCK_BLOCK = mock({'hash': MOCK_HASH})
        MOCK_HEX = 'mock hex'
        MOCK_SIG = mock({'hex': lambda: MOCK_HEX})

        KEY = 'key to sign'

        when(client).get_current_block().thenReturn(MOCK_BLOCK)
        when('plasma_cash.client.client.utils').normalize_key(KEY).thenReturn(KEY)
        when('plasma_cash.client.client').sign(MOCK_HASH, KEY).thenReturn(MOCK_SIG)

        client.submit_block(KEY)

        verify(child_chain).submit_block(MOCK_HEX)

    def test_send_transaction(self, client, child_chain):
        DUMMY_PREV_BLOCK = 'dummy prev block'
        DUMMY_UID = 5566
        DUMMY_AMOUNT = 123
        DUMMY_NEW_OWNER = 'new owner'
        DUMMY_NEW_OWNER_ADDR = 'new owner address'
        DUMMY_KEY = 'key'
        DUMMY_NORMALIZED_KEY = 'normalized key'
        MOCK_TX = mock()
        DUMMY_TX_HEX = 'dummy tx hex'
        MOCK_ENCODED_TX = mock({'hex': lambda: DUMMY_TX_HEX})

        (when('plasma_cash.client.client.utils')
            .normalize_address(DUMMY_NEW_OWNER).thenReturn(DUMMY_NEW_OWNER_ADDR))
        (when('plasma_cash.client.client.utils')
            .normalize_key(DUMMY_KEY).thenReturn(DUMMY_NORMALIZED_KEY))
        (when('plasma_cash.client.client').Transaction(
            DUMMY_PREV_BLOCK, DUMMY_UID, DUMMY_AMOUNT, DUMMY_NEW_OWNER_ADDR
            ).thenReturn(MOCK_TX))

        # `Transaction` is mocked previously, so use `any` here as a work around
        (when('plasma_cash.client.client.rlp')
            .encode(MOCK_TX, ANY)
            .thenReturn(MOCK_ENCODED_TX))

        client.send_transaction(
            DUMMY_PREV_BLOCK,
            DUMMY_UID,
            DUMMY_AMOUNT,
            DUMMY_NEW_OWNER,
            DUMMY_KEY
        )
        verify(MOCK_TX).sign(DUMMY_NORMALIZED_KEY)
        verify(child_chain).send_transaction(DUMMY_TX_HEX)

    def test_get_current_block(self, child_chain, client):
        DUMMY_BLOCK = 'dummy block'
        DUMMY_BLOCK_HEX = 'dummy block hex'
        DUMMY_DECODED_BLOCK = 'decoded block'

        when(child_chain).get_current_block().thenReturn(DUMMY_BLOCK)
        (when('plasma_cash.client.client.utils')
            .decode_hex(DUMMY_BLOCK)
            .thenReturn(DUMMY_BLOCK_HEX))
        (when('plasma_cash.client.client.rlp')
            .decode(DUMMY_BLOCK_HEX, Block)
            .thenReturn(DUMMY_DECODED_BLOCK))

        assert client.get_current_block() == DUMMY_DECODED_BLOCK

    def test_get_block(self, child_chain, client):
        DUMMY_BLOCK = 'dummy block'
        DUMMY_BLOCK_NUM = 'dummy block num'
        DUMMY_BLOCK_HEX = 'dummy block hex'
        DUMMY_DECODED_BLOCK = 'decoded block'

        when(child_chain).get_block(DUMMY_BLOCK_NUM).thenReturn(DUMMY_BLOCK)
        (when('plasma_cash.client.client.utils')
            .decode_hex(DUMMY_BLOCK)
            .thenReturn(DUMMY_BLOCK_HEX))
        (when('plasma_cash.client.client.rlp')
            .decode(DUMMY_BLOCK_HEX, Block)
            .thenReturn(DUMMY_DECODED_BLOCK))

        assert client.get_block(DUMMY_BLOCK_NUM) == DUMMY_DECODED_BLOCK

    def test_get_proof(self, child_chain, client):
        DUMMY_BLOCK_NUM = 'dummy block num'
        DUMMY_PROOF = 'dummy proof'
        DUMMY_UID = 'dummy uid'

        when(child_chain).get_proof(DUMMY_BLOCK_NUM, DUMMY_UID).thenReturn(DUMMY_PROOF)
        assert client.get_proof(DUMMY_BLOCK_NUM, DUMMY_UID) == DUMMY_PROOF

    def test_start_exit(self, client, root_chain):
        MOCK_TRANSACT = mock()
        MOCK_PREVIOUS_BLOCK = mock()
        MOCK_BLOCK = mock()

        DUMMY_EXITOR = 'dummy exitor'
        DUMMY_PREVIOUS_TX = 'dummy previous tx'
        DUMMY_ENCODED_PREVIOUS_TX = 'dummy encoded previous tx'
        DUMMY_PREVIOUS_TX_PROOF = 'dummy previous tx proof'
        DUMMY_PREVIOUS_TX_BLK_NUM = 'dummy previous tx blk num'
        DUMMY_TX = 'dummy tx'
        DUMMY_ENCODED_TX = 'dummy encoded tx'
        DUMMY_TX_PROOF = 'dummy tx proof'
        DUMMY_TX_BLK_NUM = 'dummy tx blk num'
        DUMMY_UID = 'dummy uid'

        when(w3).toChecksumAddress(DUMMY_EXITOR).thenReturn(DUMMY_EXITOR)
        when(root_chain.functions).startExit(
            DUMMY_ENCODED_PREVIOUS_TX,
            DUMMY_PREVIOUS_TX_PROOF,
            DUMMY_PREVIOUS_TX_BLK_NUM,
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(MOCK_TRANSACT)
        when(client).get_block(DUMMY_PREVIOUS_TX_BLK_NUM).thenReturn(MOCK_PREVIOUS_BLOCK)
        when(client).get_block(DUMMY_TX_BLK_NUM).thenReturn(MOCK_BLOCK)
        when(MOCK_PREVIOUS_BLOCK).get_tx_by_uid(DUMMY_UID).thenReturn(DUMMY_PREVIOUS_TX)
        when(MOCK_BLOCK).get_tx_by_uid(DUMMY_UID).thenReturn(DUMMY_TX)

        MOCK_PREVIOUS_BLOCK.merkle = mock()
        MOCK_BLOCK.merkle = mock()
        (when(MOCK_PREVIOUS_BLOCK.merkle)
            .create_merkle_proof(DUMMY_UID)
            .thenReturn(DUMMY_PREVIOUS_TX_PROOF))
        (when(MOCK_BLOCK.merkle)
            .create_merkle_proof(DUMMY_UID)
            .thenReturn(DUMMY_TX_PROOF))
        (when('plasma_cash.client.client.rlp')
            .encode(DUMMY_PREVIOUS_TX)
            .thenReturn(DUMMY_ENCODED_PREVIOUS_TX))
        (when('plasma_cash.client.client.rlp')
            .encode(DUMMY_TX)
            .thenReturn(DUMMY_ENCODED_TX))

        client.start_exit(DUMMY_EXITOR, DUMMY_UID, DUMMY_PREVIOUS_TX_BLK_NUM, DUMMY_TX_BLK_NUM)

        verify(MOCK_TRANSACT).transact({'from': DUMMY_EXITOR})

    def test_challenge_exit(self, client, root_chain):
        MOCK_BLOCK = mock()
        MOCK_TRANSACT = mock()

        DUMMY_CHALLENGER = 'dummy challenger'
        DUMMY_UID = 'dummy uid'
        DUMMY_TX = 'dummy tx'
        DUMMY_TX_PROOF = 'dummy tx proof'
        DUMMY_TX_BLK_NUM = 'dummy tx blk num'
        DUMMY_ENCODED_TX = 'dummy encoded tx'

        when(client).get_block(DUMMY_TX_BLK_NUM).thenReturn(MOCK_BLOCK)
        when(MOCK_BLOCK).get_tx_by_uid(DUMMY_UID).thenReturn(DUMMY_TX)

        MOCK_BLOCK.merkle = mock()
        (when(MOCK_BLOCK.merkle)
            .create_merkle_proof(DUMMY_UID)
            .thenReturn(DUMMY_TX_PROOF))
        (when('plasma_cash.client.client.rlp')
            .encode(DUMMY_TX)
            .thenReturn(DUMMY_ENCODED_TX))
        when(w3).toChecksumAddress(DUMMY_CHALLENGER).thenReturn(DUMMY_CHALLENGER)
        when(root_chain.functions).challengeExit(
            DUMMY_UID,
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(MOCK_TRANSACT)

        client.challenge_exit(DUMMY_CHALLENGER, DUMMY_UID, DUMMY_TX_BLK_NUM)

        verify(MOCK_TRANSACT).transact({'from': DUMMY_CHALLENGER})

    def test_respond_challenge_exit(self, client, root_chain):
        MOCK_BLOCK = mock()
        MOCK_TRANSACT = mock()

        DUMMY_RESPONDER = 'dummy responder'
        DUMMY_UID = 'dummy uid'
        DUMMY_CHALLENGE_TX = 'dummy challenge tx'
        DUMMY_TX = 'dummy tx'
        DUMMY_TX_PROOF = 'dummy tx proof'
        DUMMY_TX_BLK_NUM = 'dummy tx blk num'
        DUMMY_ENCODED_TX = 'dummy encoded tx'

        when(client).get_block(DUMMY_TX_BLK_NUM).thenReturn(MOCK_BLOCK)
        when(MOCK_BLOCK).get_tx_by_uid(DUMMY_UID).thenReturn(DUMMY_TX)

        MOCK_BLOCK.merkle = mock()
        (when(MOCK_BLOCK.merkle)
            .create_merkle_proof(DUMMY_UID)
            .thenReturn(DUMMY_TX_PROOF))
        (when('plasma_cash.client.client.rlp')
            .encode(DUMMY_TX)
            .thenReturn(DUMMY_ENCODED_TX))
        when(w3).toChecksumAddress(DUMMY_RESPONDER).thenReturn(DUMMY_RESPONDER)
        when(root_chain.functions).respondChallengeExit(
            DUMMY_UID,
            DUMMY_CHALLENGE_TX,
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(MOCK_TRANSACT)

        client.respond_challenge_exit(
            DUMMY_RESPONDER,
            DUMMY_CHALLENGE_TX,
            DUMMY_UID,
            DUMMY_TX_BLK_NUM
        )

        verify(MOCK_TRANSACT).transact({'from': DUMMY_RESPONDER})
