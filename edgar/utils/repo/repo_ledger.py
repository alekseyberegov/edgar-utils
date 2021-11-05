import abc
from typing import Tuple
from edgar.utils.date.date_utils import Date, DatePeriodType

class RepoLedger(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def start(self, date: Date) -> None:
        pass

    @abc.abstractmethod
    def end(self, date: Date) -> None:
        pass

    @abc.abstractmethod
    def error(self, date: Date, error: str) -> None:
        pass

    @abc.abstractmethod
    def record(self, period_type: DatePeriodType, the_date: Date) -> None:
        pass

    @abc.abstractmethod
    def next_period(self) -> Tuple[Date,Date]:
        pass