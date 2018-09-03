import pytest
from mockito import ANY, mock, spy, verify, when

from plasma_cash.operator_cron_job.__main__ import (APPLY_DEPOSIT_INTERVAL, SUBMIT_BLOCK_INTERVAL,
                                                    setup_job_handler)
from plasma_cash.operator_cron_job.job_handler import JobHandler
from plasma_cash.operator_cron_job.jobs.apply_deposit_job import ApplyDepositJob
from plasma_cash.operator_cron_job.jobs.submit_block_job import SubmitBlockJob
from unit_tests.unstub_mixin import UnstubMixin


class TestMain(UnstubMixin):

    @pytest.fixture(scope='function')
    def root_chain(self):
        root_chain = mock()
        deposit_filter = mock()
        (when(root_chain).eventFilter('Deposit', {'fromBlock': 0})
            .thenReturn(deposit_filter))
        when(deposit_filter).get_new_entries().thenReturn([])
        return root_chain

    @pytest.fixture(scope='function')
    def child_chain(self):
        return mock()

    def test_setup_job_handler(self, root_chain, child_chain):
        (when('plasma_cash.operator_cron_job.__main__.container')
            .get_child_chain_client().thenReturn(child_chain))

        (when('plasma_cash.operator_cron_job.__main__.container')
            .get_root_chain().thenReturn(root_chain))

        job_handler = spy(JobHandler())
        job_handler = setup_job_handler(job_handler)

        verify(job_handler).add_job(ANY(SubmitBlockJob), time_interval=SUBMIT_BLOCK_INTERVAL)
        verify(job_handler).add_job(ANY(ApplyDepositJob), time_interval=APPLY_DEPOSIT_INTERVAL)
