import pytest

from edgar.utils.date.date_utils import Date, DatePeriod, DatePeriodException, ONE_DAY, DatePeriodType
from datetime import date, timedelta
from typing import Dict

class TestDatePeriodType(object):
    def test_str_day(self):
        assert str(DatePeriodType.DAY) == "D"
    
    def test_str_quarter(self):
        assert str(DatePeriodType.QUARTER) == "Q"

    def test_from_string_day(self):
       period_type: DatePeriodType = DatePeriodType.from_string("D")
       assert period_type == DatePeriodType.DAY

    def test_from_string_quarter(self):
       period_type: DatePeriodType = DatePeriodType.from_string("Q")
       assert period_type == DatePeriodType.QUARTER


class TestDatePeriod(object):
    @pytest.mark.parametrize("period_str, expected", [
        ("D,2020-02-10,2020-03-31", "Q,2020-01-01,2020-03-31"),
        ("D,2020-01-01,2020-03-31", "Q,2020-01-01,2020-03-31"),
    ])
    def test_expand_to_quarter_success(self, period_str: str, expected: str):
        date_period = DatePeriod.from_string(period_str)
        date_period.expand_to_quarter()
        assert str(date_period) == expected

    @pytest.mark.parametrize("period_str", [
        ("D,2020-02-10,2020-04-30"),
        ("D,2020-04-01,2020-09-30"),
    ])
    def test_expand_to_quarter_fail(self, period_str: str):
        with pytest.raises(DatePeriodException):
            date_period = DatePeriod.from_string(period_str)
            date_period.expand_to_quarter()

class TestDate(object):
    @pytest.mark.parametrize("date_str", [
        ("2020-10-25"),
        ("2020-01-01"),
     ])
    def test_init_success(self, date_str):
        date_obj = Date(date_str)
        assert date_str == str(date_obj)
    
    def test_init_bad_format(self):
        with pytest.raises(ValueError):
            date_obj = Date("XXX")  

    @pytest.mark.parametrize("date_str, format_spec, expected", [
        ("2020-01-01", "QTR{q}", "QTR1"),
        ("2020-12-20", "QTR{q}", "QTR4"),
        ("2020-03-20", "{m:02}", "03"),
        ("2020-12-20", "{m:02}", "12"),
        ("2020-03-01", "{d:02}", "01"),
        ("2020-12-20", "{d:02}", "20"),
        ("2020-12-20", "{y}", "2020"),
        ("2020-11-20", "{m}", "11"),
        ("2020-03-20", "{m}", "3"),
        ("2020-03-07", "{d}", "7"),
        ("2020-03-07", "{y}-{m:02}-{d:02}", "2020-03-07"),
        ("2020-11-18", "{y}-{m:02}-{d:02}", "2020-11-18"),
    ])
    def test_format(self, date_str: str, format_spec: str, expected: str) -> None:
        date_obj = Date(date_str)
        assert date_obj.format(format_spec) == expected

    @pytest.mark.parametrize("date_str, date_period_type, args, format_spec, expected", [
        ("2020-03-07", DatePeriodType.DAY,       {},     "{t} {y}-{m:02}-{d:02}",   "D 2020-03-07"),
        ("2020-11-18", DatePeriodType.QUARTER,   {},     "{t} {y}-{m:02}-{d:02}",   "Q 2020-11-18"),
        ("2020-11-18", DatePeriodType.DAY, {"X": 9}, "{X} {t} {y}-{m:02}-{d:02}", "9 D 2020-11-18"),
    ])
    def test_format_args(self, 
            date_str: str, 
            date_period_type: DatePeriodType, 
            args: Dict,
            format_spec: str, 
            expected: str) -> None:
        date_obj = Date(date_str)
        assert date_obj.format(format_spec, date_period_type, **args) == expected

    @pytest.mark.parametrize("date_str, expected_result", [
        ("2020-01-01", 1),
        ("2020-02-01", 1),
        ("2020-03-01", 1),
        ("2020-04-01", 2),
        ("2020-05-01", 2),
        ("2020-06-01", 2),
        ("2020-07-01", 3),
        ("2020-08-01", 3),
        ("2020-09-01", 3),
        ("2020-10-01", 4),
        ("2020-11-01", 4),
        ("2020-12-01", 4),
    ])
    def test_quarter(self, date_str: str, expected_result: int):
        date_obj = Date(date_str)
        assert date_obj.quarter() == expected_result

    @pytest.mark.parametrize("from_date_str,to_date_str, expected_result", [
        ("2020-01-01", "2020-01-20", 0),
        ("2020-01-01", "2020-03-20", 0),
        ("2020-01-01", "2020-05-20", 1),
        ("2020-01-01", "2020-07-20", 2),
        ("2020-01-01", "2020-12-20", 3),
    ])
    def test_diff_quarters(self, from_date_str: str, to_date_str: str, expected_result: int):
        to_date: Date = Date(to_date_str)
        assert to_date.diff_quarters(Date(from_date_str)) == expected_result

    @pytest.mark.parametrize("from_date_str,to_date_str, expected_result", [
        ("2020-01-01", "2020-01-01",   1),
        ("2020-01-01", "2020-01-02",   2),
        ("2020-01-01", "2020-01-20",  20),
        ("2020-01-01", "2020-03-20",  80),
        ("2020-01-01", "2020-05-20", 141),
        ("2020-01-01", "2020-07-20", 202),
        ("2020-01-01", "2020-12-20", 355),
    ])
    def test_diff_days(self, from_date_str: str, to_date_str: str, expected_result: int):
        to_date: Date = Date(to_date_str)
        assert to_date.diff_days(Date(from_date_str)) == expected_result

    @pytest.mark.parametrize("from_date_str,to_date_str,has_backfill", [
        ("2020-01-10", "2020-01-09", False),
        ("2020-01-10", "2020-01-10", True),
        ("2020-01-10", "2020-01-01", False),
        ("2020-03-01", "2020-01-01", False),
    ])
    def test_backfill_same_date(self, from_date_str,to_date_str,has_backfill):
        to_date: Date = Date(to_date_str)
        from_date: Date = Date(from_date_str)

        for _ in to_date.backfill(from_date):
            assert has_backfill, "should return an empty iterator"
            return
        assert not has_backfill

    @pytest.mark.parametrize("from_date_str,to_date_str, grain_expected, num_expected", [
        ("2020-01-01", "2020-01-20", DatePeriodType.DAY, 20),
        ("2020-01-01", "2020-01-25", DatePeriodType.DAY, 25),
        ("2020-01-01", "2020-01-02", DatePeriodType.DAY,  2),
        ("2020-01-01", "2020-01-01", DatePeriodType.DAY,  1),
    ])
    def test_backfill_same_quarter(self, from_date_str: str, to_date_str: str, grain_expected: str, num_expected: int):
        to_date: Date = Date(to_date_str)
        from_date: Date = Date(from_date_str)

        had_results = False
        for date_period in to_date.backfill(from_date):
            had_results = True
            assert date_period.period_type == grain_expected
            assert date_period.num_days == num_expected
            assert date_period.start_date == from_date
            assert date_period.end_date == to_date
        assert had_results

    @pytest.mark.parametrize("from_date_str, to_date_str, elems", [
        ("2020-01-10", "2020-04-20",   "DD"),
        ("2020-01-10", "2020-07-20",  "DQD"),
        ("2020-01-01", "2020-03-31",    "Q"),
        ("2020-01-01", "2020-12-31", "QQQQ"),
        ("2020-01-01", "2020-12-30", "QQQD"),
        ("2020-01-02", "2020-10-20", "DQQD"),
        ("2020-01-01", "2020-06-30",   "QQ"),
        ("2020-01-10", "2020-06-20",   "DD"),
    ])
    def test_backfill_diff_quarters(self, from_date_str, to_date_str, elems):
        to_date: Date = Date(to_date_str)
        from_date: Date = Date(from_date_str)

        items : str = ""
        for date_period in to_date.backfill(from_date):
            items += str(date_period.period_type)
        assert items == elems

    @pytest.mark.parametrize("date_str, expected_quarter_start, expected_quarter_end", [
        ("2020-01-01", "2020-01-01", "2020-03-31"),
        ("2020-03-30", "2020-01-01", "2020-03-31"),
        ("2020-03-31", "2020-01-01", "2020-03-31"),
        ("2020-04-01", "2020-04-01", "2020-06-30"),
        ("2020-06-30", "2020-04-01", "2020-06-30"),
        ("2020-07-01", "2020-07-01", "2020-09-30"),
        ("2020-09-01", "2020-07-01", "2020-09-30"),
        ("2020-09-30", "2020-07-01", "2020-09-30"),
        ("2020-10-01", "2020-10-01", "2020-12-31"),
        ("2020-11-01", "2020-10-01", "2020-12-31"),
        ("2020-12-30", "2020-10-01", "2020-12-31"),
        ("2020-12-31", "2020-10-01", "2020-12-31"),
    ])
    def test_quarter_dates(self, date_str: str, expected_quarter_start: str, expected_quarter_end: str):
        date_obj: Date = Date(date_str)
        assert date_obj.quarter_dates() == (
            Date(expected_quarter_start),
            Date(expected_quarter_end))

    @pytest.mark.parametrize("date_str, expected_result, days", [
        ("2020-01-01", "2020-01-01",  0),
        ("2020-01-01", "2020-01-20", 19),
        ("2020-01-01", "2020-01-31", 30),
        ("2020-01-01", "2020-02-01", 31),
        ("2020-01-01", "2020-02-02", 32),
    ])
    def test_add_days(self, date_str: str, expected_result: str, days: int):
        date_obj: Date = Date(date_str)
        date_new: Date = date_obj.add_days(days)
        assert str(date_new) == expected_result

    @pytest.mark.parametrize("from_date_str, to_date_str, days", [
        ("2020-01-01", "2020-01-01",  1),
        ("2020-01-01", "2020-01-20", 20),
        ("2020-01-01", "2020-01-31", 31),
        ("2020-01-01", "2020-02-01", 32),
        ("2020-01-01", "2020-02-02", 33),
    ])
    def test_add_days(self, from_date_str: str, to_date_str: str,  days: int) -> None:
        from_date: Date = Date(from_date_str)
        to_date: Date = Date(to_date_str)
        count: int = 0
        while from_date <= to_date:
            from_date += 1
            count += 1
        assert count == days

    @pytest.mark.parametrize("date_str, dayofweek, whichweek, expected_result", [
        ("2020-01-02", 1, 1, "2020-01-06"),
        ("2020-01-02", 2, 1, "2020-01-07"),
        ("2020-01-02", 3, 1, "2020-01-01"),
        ("2020-01-02", 4, 1, "2020-01-02"),
        ("2020-01-01", 5, 1, "2020-01-03"),
        ("2020-01-01", 6, 1, "2020-01-04"),
        ("2020-01-01", 7, 1, "2020-01-05"),
        ("2020-01-01", 1, 2, "2020-01-13"),
        ("2020-01-01", 2, 2, "2020-01-14"),
        ("2020-01-01", 3, 2, "2020-01-08"),
        ("2020-01-02", 4, 2, "2020-01-09"),
        ("2020-01-02", 5, 2, "2020-01-10"),
        ("2020-01-02", 6, 2, "2020-01-11"),
        ("2020-01-01", 7, 2, "2020-01-12"),
        ("2020-01-01", 1, 4, "2020-01-27"),
        ("2020-01-01", 4, 5, "2020-01-30"),
        ("2020-01-01", 1, 5, "2020-01-27"),
        ("2020-12-13", 1, 5, "2020-12-28"),
    ])
    def test_nthday_of_nthweek(self, date_str: str, dayofweek: int, whichweek: int, expected_result: str) -> None:
        date_obj: Date = Date(date_str)
        date_new: Date = date_obj.nthday_of_nthweek(dayofweek=dayofweek, whichweek=whichweek)
        assert str(date_new) == expected_result

    @pytest.mark.parametrize("date_str, expected_result", [
        ("2020-01-01", False),
        ("2020-02-02", True),
        ("2020-03-28", True),
    ]) 
    def is_weekend(self, date_str: str, expected_result: bool) -> None:
        date_obj: Date = Date(date_str)
        assert date_obj.is_weekend() == expected_result


