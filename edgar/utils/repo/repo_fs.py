import abc
from dataclasses import dataclass
from typing import Iterator, List, Dict, Tuple

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
        >>> master{y:04}{m:02}{d:02}.idx
    """
    name_spec: Dict[DatePeriodType, str] 

    """
        The path specification for objects in the repository.

        Examples
        --------
        >>> ['{t}', '{y}', 'QTR{q}']
    """
    path_spec: List[str]


class RepoFormatter:
    def __init__(self, format: RepoFormat) -> None:
        self.__format = format
        self.__macros = {}

    def __setitem__(self, key, val):
        self.__macros[key] = val

    def format(self, period_type: DatePeriodType, the_date: Date, **kwargs) -> List[str]:
        name_spec = self.__format.name_spec[period_type]
        path_spec = self.__format.path_spec

        eval_macros = dict(kwargs)
        for name, func in self.__macros.items():
            eval_macros[name] = func(period_type, the_date)

        return [*[the_date.format(s, period_type, **eval_macros) for s in path_spec], 
            the_date.format(name_spec, period_type, **eval_macros)]


class RepoEntity(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def exists(self) -> bool:
        pass

    @abc.abstractmethod
    def as_uri(self) -> str:
        pass

class RepoObject(RepoEntity, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def inp(self, bufsize: int) -> Iterator[str]:
        pass

    @abc.abstractmethod
    def out(self, iter: Iterator[str], override: bool = False) -> None:
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
    from edgar.utils.repo.repo_object_path import RepoObjectPath
    @abc.abstractmethod
    def iterate_missing(self, from_date: Date, to_date: Date) -> Iterator[RepoObjectPath]:
        pass

    @abc.abstractmethod
    def find_missing(self, from_date: Date, to_date: Date) -> List[str]:
        pass

    @abc.abstractmethod
    def find(self, period_type: DatePeriodType, the_date: Date) -> RepoObject:
        pass

    @abc.abstractmethod
    def create(self, period_type: DatePeriodType, the_date: Date) -> RepoObject:
        pass

    @abc.abstractmethod
    def refresh(self) -> None:
        pass

class RepoDirVisitor(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def visit(self, object: RepoObject) -> bool:
        pass

class RepoTransaction(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self, date: Date) -> None:
        pass

    @abc.abstractmethod
    def commit(self, date: Date) -> None:
        pass

    def error(self, date: Date, error: str) -> None:
        pass
    
    @abc.abstractmethod
    def create(self, period_type: DatePeriodType, the_date: Date) -> None:
        pass

    @abc.abstractmethod
    def date_range(self) -> Tuple[Date,Date]:
        pass
