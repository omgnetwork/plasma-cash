import pytest
from mockito import mock, verify, when

from plasma_cash.operator_cron_job.jobs.apply_deposit_job import ApplyDepositJob
from unit_tests.unstub_mixin import UnstubMixin


class TestApplyDepositJob(UnstubMixin):

    @pytest.fixture(scope='function')
    def root_chain(self):
        return mock()

    @pytest.fixture(scope='function')
    def child_chain(self):
        return mock()

    def test_run(self, root_chain, child_chain):
        deposit_filter = mock()
        (when(root_chain).eventFilter('Deposit', {'fromBlock': 0})
            .thenReturn(deposit_filter))

        DUMMY_DEPOSITOR = 'dummy depositor'
        DUMMY_AMOUNT = 100
        DUMMY_UID = 0
        events = [{
            'args': {
                'depositor': DUMMY_DEPOSITOR, 'amount': DUMMY_AMOUNT, 'uid': DUMMY_UID
            }}
        ]
        when(deposit_filter).get_new_entries().thenReturn(events)

        job = ApplyDepositJob(root_chain, child_chain)
        job.run()

        verify(child_chain).apply_deposit(DUMMY_DEPOSITOR, DUMMY_AMOUNT, DUMMY_UID)
