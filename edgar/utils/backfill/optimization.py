import abc

from typing import List
from edgar.utils.date.date_utils import DatePeriod

class BackfillOptimization(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def capture(self, backfill: DatePeriod) -> None:
        pass

    @abc.abstractmethod
    def optimize(self) -> List[DatePeriod]:
        pass