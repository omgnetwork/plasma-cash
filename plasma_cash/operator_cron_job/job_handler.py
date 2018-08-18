import time
from threading import Thread


class JobHandler(object):
    def __init__(self):
        self.workers = []

    def add_job(self, job, time_interval):
        worker = Thread(target=self._schedule_the_job, args=(job, time_interval,), daemon=True)
        self.workers.append(worker)

    def start(self):
        for worker in self.workers:
            worker.start()

    def _schedule_the_job(self, job, time_interval):
        while True:
            job.run()
            time.sleep(time_interval)
