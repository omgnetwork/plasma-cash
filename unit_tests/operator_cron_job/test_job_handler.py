import time

import pytest

from plasma_cash.operator_cron_job.job_handler import JobHandler
from plasma_cash.operator_cron_job.jobs.job_interface import JobInterface
from unit_tests.unstub_mixin import UnstubMixin


class FakeJob(JobInterface):

    def __init__(self):
        self.run_count = 0

    def run(self):
        self.run_count += 1


class TestJobHandler(UnstubMixin):

    @pytest.fixture(scope='function')
    def job_handler(self):
        return JobHandler()

    def test_add_job(self, job_handler):
        job = FakeJob()
        job_handler.add_job(job, 1)
        assert len(job_handler.workers) == 1

    def test_start(self, job_handler):
        job = FakeJob()

        JOB_TIME_INTERVAL = 0.05
        job_handler.add_job(job, JOB_TIME_INTERVAL)
        job_handler.start()

        SLIGHLY_LONGER_INTERVAL_FOR_RUN_JOB_TWICE = JOB_TIME_INTERVAL + 0.001
        time.sleep(SLIGHLY_LONGER_INTERVAL_FOR_RUN_JOB_TWICE)
        assert job.run_count == 2
