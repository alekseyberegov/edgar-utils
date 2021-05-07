import abc
from dataclasses import dataclass
from typing import Tuple, Iterator, Generator, List, Dict

from edgar.utils.date.date_utils import Date, DatePeriodType

@dataclass
class RepoFormat:
    """
        The object name specifications by the date period type
        
        Available macros are:
                    - {q} for the quarter
                    - {d} for the day number
                    - {m} for the month number
                    - {y} for the 4-digit year number
                    - {t} for the date period type

        Examples
        -------- 
        >>> master{y}{m:02}{d:02}.idx
    """
    name_spec: Dict[DatePeriodType, str] 

    """
        The path specification for objects in the repository.
    """
    path_spec: List[str]


class RepoEntity(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

class RepoObject(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def inp(self, bufsize: int) -> Generator[str, None, None]:
        pass

    @abc.abstractmethod
    def out(self, iter: Iterator, override: bool = False) -> None:
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

    @abc.abstractmethod
    def refresh(self) -> None:
        pass

class RepoFS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def check_updates(self, from_date: Date, to_date: Date) -> List[str]:
        pass

    @abc.abstractmethod
    def find(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:        
        pass

    @abc.abstractmethod
    def create(self, date_period: DatePeriodType, the_date: Date) -> RepoObject:
        pass

    @abc.abstractmethod
    def refresh(self) -> None:
        pass