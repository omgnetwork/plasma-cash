import pytest
from ethereum import utils
from ethereum.tools import tester

from plasma_cash.root_chain.deployer import Deployer
from unit_tests.unstub_mixin import UnstubMixin


class TestRootChain(UnstubMixin):

    @pytest.fixture(scope='class')
    def tester_chain(self):
        tester.chain = tester.Chain()
        return tester

    @pytest.fixture(scope='class')
    def contract(self, tester_chain):
        deployer = Deployer()
        abi, bytecode, contract_name = deployer.compile_contract('RootChain/RootChain.sol')
        address = tester_chain.chain.tx(
            sender=tester_chain.k0,
            to=b'',
            startgas=(4 * 10**6),
            value=0,
            data=utils.decode_hex(bytecode)
        )
        tester_chain.chain.mine()
        return tester_chain.ABIContract(tester_chain.chain, abi, address)

    def test_submit_block(self, tester_chain, contract):
        DUMMY_MERKLE_ROOT = b'\x00' * 32
        DUMMY_BLK_NUM = 1

        assert contract.currentBlkNum() == 0
        contract.submitBlock(DUMMY_MERKLE_ROOT, DUMMY_BLK_NUM, sender=tester_chain.k0)
        assert contract.currentBlkNum() == 1
        assert contract.childChain(DUMMY_BLK_NUM) == DUMMY_MERKLE_ROOT

    def test_deposit(self, tester_chain, contract):
        DUMMY_AMOUNT = 10
        DUMMY_ZERO_ADDRESS = '0x' + '00' * 20

        assert contract.depositCount() == 0
        uid = contract.deposit(
            DUMMY_ZERO_ADDRESS,
            DUMMY_AMOUNT,
            value=DUMMY_AMOUNT * 10**18,
            sender=tester_chain.k1
        )
        assert contract.depositCount() == 1
        assert contract.wallet(uid) == [True, False, DUMMY_AMOUNT, '0x' + tester_chain.a1.hex()]
