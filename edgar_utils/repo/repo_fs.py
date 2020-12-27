import abc
from typing import Tuple, Iterator, Generator, List, Dict

from edgar_utils.date.date_utils import Date, DatePeriodType

class RepoEntity(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

class RepoObject(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def iter_content(self, bufsize: int) -> Generator[str, None, None]:
        pass

    @abc.abstractmethod
    def write_content(self, iter: Iterator, override: bool = False) -> None:
        pass

    @abc.abstractmethod
    def subpath(self, levels: int) -> List[str]:
        pass

class RepoDir(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def new_object(self, name: str) -> RepoObject:
        pass

    @abc.abstractmethod
    def new_dir(self, name: str) -> 'RepoDir':
        pass

class RepoFS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_update_list(self, from_date: Date, to_date: Date) -> List[str]:
        pass

    @abc.abstractmethod
    def get_object(self, rel_path: str) -> RepoObject:
        pass

    @abc.abstractmethod
    def new_object(self, rel_path: str, object_name: str) -> RepoObject:
        pass

    @abc.abstractmethod
    def refresh(self) -> None:
        pass