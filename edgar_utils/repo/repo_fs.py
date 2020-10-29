import abc
from typing import Tuple, Iterator, Generator, List

from edgar_utils.date.date_utils import Date, DatePeriodType

class RepoEntity(metaclass=abc.ABCMeta):
    pass

class RepoObject(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def iter_content(self, bufsize: int) -> Generator[str, None, None]:
        pass

    @abc.abstractmethod
    def write_content(self, iter: Iterator, override: bool = False) -> None:
        pass

class RepoDir(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    @abc.abstractmethod
    def new_object(self, name: str) -> RepoObject:
        pass

    @abc.abstractmethod
    def new_dir(self, name: str) -> 'RepoDir':
        pass

class RepoFS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def years(self, period_type: DatePeriodType) -> List[int]:
        pass

    @abc.abstractmethod
    def push(self, remote_repo: 'RepoFS') -> None:
        pass

    @abc.abstractmethod
    def pull(self, remote_repo: 'RepoFS') -> None:
        pass
