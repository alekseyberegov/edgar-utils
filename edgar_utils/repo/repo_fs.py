import abc
from typing import Tuple, Iterator, Generator, List, Dict

from edgar_utils.date.date_utils import Date, DatePeriodType
from dataclasses import dataclass

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
    object_specs: Dict[DatePeriodType, str] 

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