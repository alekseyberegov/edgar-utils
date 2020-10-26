from typing import List

from edgar_utils.backfill.optimization import BackfillOptimization
from edgar_utils.date.date_utils import DatePeriod, DatePeriodType

class MinimizeDownloadsBackfill(BackfillOptimization):
    def __init__(self, max_days: int = 15) -> None:
        self.periods : List[DatePeriod] = []
        self.max_days = max_days

    def capture(self, backfill: DatePeriod) -> None:
        self.periods.append(backfill)

    def optimize(self) -> List[DatePeriod]:
        for date_period in self.periods:
            if date_period.period_type == DatePeriodType.DAY:
                if date_period.num_days > self.max_days:
                    date_period.expand_to_quarter()

        return self.periods