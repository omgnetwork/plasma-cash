import pytest
from mockito import ANY, mock, verify, when

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
        DUMMY_KEY = '0xa18969817c2cefadf52b93eb20f917dce760ce13b2ac9025e0361ad1e7a1d448'
        return Client(root_chain, child_chain, DUMMY_KEY)

    def test_constructor(self):
        DUMMY_ROOT_CHAIN = 'root chain'
        DUMMY_CHILD_CHAIN = 'child chain'
        DUMMY_KEY = 'key'

        when('plasma_cash.client.client.utils').normalize_key(DUMMY_KEY).thenReturn(DUMMY_KEY)
        c = Client(DUMMY_ROOT_CHAIN, DUMMY_CHILD_CHAIN, DUMMY_KEY)

        assert c.root_chain == DUMMY_ROOT_CHAIN
        assert c.child_chain == DUMMY_CHILD_CHAIN
        assert c.key == DUMMY_KEY

    def test_address(self, client):
        DUMMY_ADDRESS = '0x3B0884f4E50e9BC2CE9b224aB72feA89a81CDF7c'

        assert client.address == DUMMY_ADDRESS

    def test_sign_and_send_tx(self, client):
        DUMMY_NONCE = 123
        DUMMY_TX = {
            'gas': 100,
            'gasPrice': 100,
            'nonce': DUMMY_NONCE
        }
        (when('plasma_cash.client.client.w3.eth')
            .getTransactionCount(ANY, ANY).thenReturn(DUMMY_NONCE))
        when('plasma_cash.client.client.w3.eth').sendRawTransaction(ANY).thenReturn(None)

        client._sign_and_send_tx(DUMMY_TX)

        verify('plasma_cash.client.client.w3.eth').sendRawTransaction(ANY)

    def test_deposit(self, client, root_chain):
        DUMMY_AMOUNT = 1
        DUMMY_CURRENCY = '0x0000000000000000000000000000000000000000'

        MOCK_FUNCTION = mock()
        TX = mock()
        when(root_chain.functions).deposit(DUMMY_CURRENCY, DUMMY_AMOUNT).thenReturn(MOCK_FUNCTION)
        when(MOCK_FUNCTION).buildTransaction({
            'from': client.address,
            'value': DUMMY_AMOUNT * 10**18
        }).thenReturn(TX)
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.deposit(DUMMY_AMOUNT, DUMMY_CURRENCY)

        verify(client)._sign_and_send_tx(ANY)

    def test_submit_block(self, client, child_chain):
        MOCK_HASH = 'mock hash'
        MOCK_BLOCK = mock({'hash': MOCK_HASH})
        MOCK_HEX = 'mock hex'
        MOCK_SIG = mock({'hex': lambda: MOCK_HEX})

        when(client).get_current_block().thenReturn(MOCK_BLOCK)
        when('plasma_cash.client.client').sign(MOCK_HASH, client.key).thenReturn(MOCK_SIG)
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.submit_block()

        verify(child_chain).submit_block(MOCK_HEX)

    def test_send_transaction(self, client, child_chain):
        DUMMY_PREV_BLOCK = 'dummy prev block'
        DUMMY_UID = 5566
        DUMMY_AMOUNT = 123
        DUMMY_NEW_OWNER = 'new owner'
        DUMMY_NEW_OWNER_ADDR = 'new owner address'
        MOCK_TX = mock()
        DUMMY_TX_HEX = 'dummy tx hex'
        MOCK_ENCODED_TX = mock({'hex': lambda: DUMMY_TX_HEX})

        (when('plasma_cash.client.client.utils')
            .normalize_address(DUMMY_NEW_OWNER).thenReturn(DUMMY_NEW_OWNER_ADDR))
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
            DUMMY_NEW_OWNER
        )
        verify(MOCK_TX).sign(client.key)
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

    def test_get_proof(self, child_chain, client):
        DUMMY_BLOCK_NUM = 'dummy block num'
        DUMMY_PROOF = 'dummy proof'
        DUMMY_UID = 'dummy uid'

        when(child_chain).get_proof(DUMMY_BLOCK_NUM, DUMMY_UID).thenReturn(DUMMY_PROOF)
        assert client.get_proof(DUMMY_BLOCK_NUM, DUMMY_UID) == DUMMY_PROOF

    def test_start_exit(self, client, root_chain):
        MOCK_PREVIOUS_BLOCK = mock()
        MOCK_BLOCK = mock()

        DUMMY_PREVIOUS_TX = 'dummy previous tx'
        DUMMY_ENCODED_PREVIOUS_TX = 'dummy encoded previous tx'
        DUMMY_PREVIOUS_TX_PROOF = 'dummy previous tx proof'
        DUMMY_PREVIOUS_TX_BLK_NUM = 'dummy previous tx blk num'
        DUMMY_TX = 'dummy tx'
        DUMMY_ENCODED_TX = 'dummy encoded tx'
        DUMMY_TX_PROOF = 'dummy tx proof'
        DUMMY_TX_BLK_NUM = 'dummy tx blk num'
        DUMMY_UID = 'dummy uid'

        when(root_chain.functions).startExit(
            DUMMY_ENCODED_PREVIOUS_TX,
            DUMMY_PREVIOUS_TX_PROOF,
            DUMMY_PREVIOUS_TX_BLK_NUM,
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(mock())
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
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.start_exit(DUMMY_UID, DUMMY_PREVIOUS_TX_BLK_NUM, DUMMY_TX_BLK_NUM)

        verify(client)._sign_and_send_tx(ANY)

    def test_abort_deposit(self, client, root_chain):
        DUMMY_UID = 'dummy uid'
        when(root_chain.functions).abortDeposit(DUMMY_UID).thenReturn(mock())
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.abort_deposit(DUMMY_UID)
        verify(client)._sign_and_send_tx(ANY)

    def test_start_deposit_exit(self, client, root_chain):
        MOCK_BLOCK = mock()

        DUMMY_TX = 'dummy tx'
        DUMMY_ENCODED_TX = 'dummy encoded tx'
        DUMMY_TX_PROOF = 'dummy tx proof'
        DUMMY_TX_BLK_NUM = 'dummy tx blk num'
        DUMMY_UID = 'dummy uid'

        when(root_chain.functions).startDepositExit(
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(mock())
        when(client).get_block(DUMMY_TX_BLK_NUM).thenReturn(MOCK_BLOCK)
        when(MOCK_BLOCK).get_tx_by_uid(DUMMY_UID).thenReturn(DUMMY_TX)

        MOCK_BLOCK.merkle = mock()
        (when(MOCK_BLOCK.merkle)
            .create_merkle_proof(DUMMY_UID)
            .thenReturn(DUMMY_TX_PROOF))
        (when('plasma_cash.client.client.rlp')
            .encode(DUMMY_TX)
            .thenReturn(DUMMY_ENCODED_TX))
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.start_deposit_exit(DUMMY_UID, DUMMY_TX_BLK_NUM)

        verify(client)._sign_and_send_tx(ANY)

    def test_challenge_exit(self, client, root_chain):
        MOCK_BLOCK = mock()

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
        when(root_chain.functions).challengeExit(
            DUMMY_UID,
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(mock())
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.challenge_exit(DUMMY_UID, DUMMY_TX_BLK_NUM)

        verify(client)._sign_and_send_tx(ANY)

    def test_respond_challenge_exit(self, client, root_chain):
        MOCK_BLOCK = mock()

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
        when(root_chain.functions).respondChallengeExit(
            DUMMY_UID,
            DUMMY_CHALLENGE_TX,
            DUMMY_ENCODED_TX,
            DUMMY_TX_PROOF,
            DUMMY_TX_BLK_NUM
        ).thenReturn(mock())
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.respond_challenge_exit(DUMMY_CHALLENGE_TX, DUMMY_UID, DUMMY_TX_BLK_NUM)

        verify(client)._sign_and_send_tx(ANY)

    def test_finalize_exit(self, client, root_chain):
        DUMMY_UID = 'dummy uid'

        when(root_chain.functions).finalizeExit(DUMMY_UID).thenReturn(mock())
        when(client)._sign_and_send_tx(ANY).thenReturn(None)

        client.finalize_exit(DUMMY_UID)

        verify(client)._sign_and_send_tx(ANY)
