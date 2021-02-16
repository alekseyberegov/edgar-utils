import pytest
from edgar_utils.date.holidays import us_holidays
from edgar_utils.date.date_utils import Date
from typing import Dict

class TestHolidays(object):
    @pytest.mark.parametrize("date_str, expected_result", [
        ("2020-01-01", True),
        ("2020-01-20", True),
        ("2020-02-17", True),
        ("2020-05-25", True),
        ("2020-07-03", True),
        ("2020-09-07", True),
        ("2020-11-11", True),
        ("2020-11-26", True),
        ("2020-12-25", True),
        ("2020-01-25", False),
    ])
    def test_contains(self, date_str: str, expected_result: bool) -> None:
        date_obj: Date = Date(date_str)
        holidays: us_holidays = us_holidays(date_obj.year())
        assert (date_obj in holidays) == expected_result

    def test_iterator(self) -> None:
        date_obj: Date = Date("2020-01-01")
        holidays: us_holidays = us_holidays(date_obj.year())
        dates: Dict[str, bool] = {}
        for i in holidays:
            dates[str(i)] = True

        assert ("2020-01-01") in dates
        assert ("2020-01-20") in dates
        assert ("2020-02-17") in dates
        assert ("2020-05-25") in dates
        assert ("2020-07-03") in dates
        assert ("2020-09-07") in dates
        assert ("2020-11-11") in dates
        assert ("2020-11-26") in dates
        assert ("2020-12-25") in dates

    @pytest.mark.parametrize("date_str, expected_result", [
        ("2020-01-01", 'New Year''s Day'),
        ("2020-01-20", 'Birthday of Martin Luther King, Jr.'),
        ("2020-02-17", 'Washington''s Birthday'),

    ])
    def test_name(self, date_str: str, expected_result: str) -> None:
        holidays: us_holidays = us_holidays(2020)
        assert (holidays << date_str) == expected_result

