import pytest
from edgar_utils.date.holidays import USHoliday
from edgar_utils.date.date_utils import Date

class TestUSHoliday(object):
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
    def test_in_holidays(self, date_str: str, expected_result: bool) -> None:
        date_obj: Date = Date(date_str)
        holidays: USHoliday = USHoliday(date_obj.date_inst.year)
        assert (date_obj in holidays) == expected_result
