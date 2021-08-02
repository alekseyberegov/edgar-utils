import abc
from typing import Iterator, List, Dict, Tuple
from edgar.utils.date.date_utils import Date, DatePeriodType

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


class RepoURI(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def date(self) -> Date:
        pass

    @abc.abstractmethod
    def date_period_type(self) -> DatePeriodType:
        pass

    @abc.abstractmethod
    def quarter(self) -> int:
        pass

    @abc.abstractmethod
    def year(self) -> int:
        pass


class RepoFS(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def iterate_missing(self, from_date: Date, to_date: Date) -> Iterator[RepoURI]:
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

    @abc.abstractmethod
    def error(self, date: Date, error: str) -> None:
        pass
    
    @abc.abstractmethod
    def create(self, period_type: DatePeriodType, the_date: Date) -> None:
        pass

    @abc.abstractmethod
    def date_range(self) -> Tuple[Date,Date]:
        pass
