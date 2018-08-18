from plasma_cash.config import plasma_config
from plasma_cash.dependency_config import container

from .job_handler import JobHandler
from .jobs.apply_deposit_job import ApplyDepositJob
from .jobs.submit_block_job import SubmitBlockJob

SUBMIT_BLOCK_INTERVAL = 5
APPLY_DEPOSIT_INTERVAL = 1


def setup_job_handler(job_handler):
    root_chain = container.get_root_chain()
    child_chain_client = container.get_child_chain_client()

    apply_deposit_job = ApplyDepositJob(root_chain, child_chain_client)
    submit_block_job = SubmitBlockJob(child_chain_client, plasma_config['AUTHORITY_KEY'])

    job_handler.add_job(submit_block_job, time_interval=SUBMIT_BLOCK_INTERVAL)
    job_handler.add_job(apply_deposit_job, time_interval=APPLY_DEPOSIT_INTERVAL)

    return job_handler


if __name__ == '__main__':
    job_handler = JobHandler()
    job_handler = setup_job_handler(job_handler)
    job_handler.start()
