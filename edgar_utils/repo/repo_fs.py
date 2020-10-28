import abc
from typing import Tuple, Iterator

from edgar_utils.date.date_utils import Date

class RepoEntity(metaclass=abc.ABCMeta):
    pass

class RepoObject(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def iter_content(self, bufsize: int) -> Iterator:
        pass

    @abc.abstractmethod
    def write_content(self, iter: Iterator) -> None:
        pass

class RepoDir(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def child_count(self) -> int:
        pass
    
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    @abc.abstractmethod
    def new_object(self, name: str) -> RepoObject:
        pass

class RepoFS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_quarterly_file(self, year: int, quarter: int) -> RepoObject:
        pass

    @abc.abstractmethod
    def put_quarterly_file(self, year: int, quarter: int, the_file: RepoObject) -> None:
        pass

    @abc.abstractmethod
    def get_daily_file(self, the_date: Date) -> RepoObject:
        pass

    @abc.abstractmethod
    def put_daily_file(self, the_date: Date, the_file: RepoObject) -> None:
        pass

    @abc.abstractmethod
    def push(self, remote_repo: 'RepoFS') -> None:
        pass

    @abc.abstractmethod
    def pull(self, remote_repo: 'RepoFS') -> None:
        pass
