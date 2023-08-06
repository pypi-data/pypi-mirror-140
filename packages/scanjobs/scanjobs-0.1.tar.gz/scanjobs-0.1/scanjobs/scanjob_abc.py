import abc


class ScanJob(abc.ABC):

    def to_queue(self) -> str:
        pass

    def from_queue(self, job_string):
        pass
