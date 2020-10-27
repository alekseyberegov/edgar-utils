import abc
from typing import Tuple

from edgar_utils.date.date_utils import Date

class RepoFile(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def open(self):
        pass

class RepoFS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_quarterly_file(self, year: int, quarter: int) -> RepoFile:
        pass

    @abc.abstractmethod
    def put_quarterly_file(self, year: int, quarter: int, the_file: RepoFile) -> None:
        pass

    @abc.abstractmethod
    def get_daily_file(self, the_date: Date) -> RepoFile:
        pass

    @abc.abstractmethod
    def put_daily_file(self, the_date: Date, the_file: RepoFile) -> None:
        pass

    @abc.abstractmethod
    def push(self, remote_repo: 'RepoFS') -> None:
        pass

    @abc.abstractmethod
    def pull(self, remote_repo: 'RepoFS') -> None:
        pass
