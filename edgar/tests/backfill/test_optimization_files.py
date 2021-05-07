import pytest

from edgar.utils.backfill.optimization_files import MinimizeDownloadsBackfill
from edgar.utils.date.date_utils import Date, DatePeriod, DatePeriodType
from typing import List

class TestMinimizeDownloadsBackfill(object):

    @pytest.mark.parametrize("date_period_str, expected_result", [
        ("D,2020-02-10,2020-03-31", "Q,2020-01-01,2020-03-31"),
        ("D,2020-01-05,2020-03-31", "Q,2020-01-01,2020-03-31"),
        ("D,2020-03-05,2020-03-31", "Q,2020-01-01,2020-03-31"),
        ("D,2020-03-31,2020-03-31", "D,2020-03-31,2020-03-31"),
        ("D,2020-01-05,2020-01-15", "D,2020-01-05,2020-01-15"),
    ])
    def test_optimize(self, date_period_str: str, expected_result: str):
        optimize: MinimizeDownloadsBackfill = MinimizeDownloadsBackfill(max_days=20)
        optimize.capture(DatePeriod.from_string(date_period_str))
        date_periods: List[DatePeriod] = optimize.optimize()
        assert len(date_periods) == 1
        assert str(date_periods[0]) == expected_result

    @pytest.mark.parametrize("date_period_str, expected_result", [
        (["D,2020-02-10,2020-03-31", "Q,2020-01-01,2020-03-31"], ["Q,2020-01-01,2020-03-31", "Q,2020-01-01,2020-03-31"]),
    ])
    def test_optimize_multiperiod(self, date_period_str: List[str], expected_result: List[str]):
        optimize: MinimizeDownloadsBackfill = MinimizeDownloadsBackfill(max_days=20)
        for s in date_period_str:
            optimize.capture(DatePeriod.from_string(s))
        date_periods: List[DatePeriod] = optimize.optimize()
        for i in range(2):
            assert str(date_periods[i]) == expected_result[i]

                

