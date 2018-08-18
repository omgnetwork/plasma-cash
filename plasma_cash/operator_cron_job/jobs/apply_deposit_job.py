from .job_interface import JobInterface


class ApplyDepositJob(JobInterface):

    def __init__(self, root_chain, child_chain):
        self.child_chain = child_chain
        self.deposit_filter = root_chain.eventFilter('Deposit', {'fromBlock': 0})

    def run(self):
        for event in self.deposit_filter.get_new_entries():
            depositor = event['args']['depositor']
            amount = event['args']['amount']
            uid = event['args']['uid']
            self.child_chain.apply_deposit(depositor, amount, uid)
