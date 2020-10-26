import pytest

from edgar_utils.date.date_utils import Date
from datetime import date

class TestDate(object):
    def test_init_success(self):
        date_str = "2020-10-25"
        date_obj = Date(date_str)
        assert date_str == str(date_obj)
    
    def test_init_bad_format(self):
        try:
            date_obj = Date("XXX")
            assert False
        except ValueError:
            assert True

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
    def test_diff_quarter(self, from_date_str: str, to_date_str: str, expected_result: int):
        to_date: Date = Date(to_date_str)
        assert to_date.diff_quarter(Date(from_date_str)) == expected_result

    @pytest.mark.parametrize("from_date_str,to_date_str, expected_result", [
        ("2020-01-01", "2020-01-20",  19),
        ("2020-01-01", "2020-03-20",  79),
        ("2020-01-01", "2020-05-20", 140),
        ("2020-01-01", "2020-07-20", 201),
        ("2020-01-01", "2020-12-20", 354),
    ])
    def test_diff_days(self, from_date_str: str, to_date_str: str, expected_result: int):
        to_date: Date = Date(to_date_str)
        assert to_date.diff_days(Date(from_date_str)) == expected_result

    def test_backfill_same_date(self):
        to_date: Date = Date("2020-10-20")
        from_date: Date = Date("2020-10-20")

        for s in to_date.backfill(from_date):
            assert False, "should return an empty iterator"
        assert True

    @pytest.mark.parametrize("from_date_str,to_date_str, grain_expected, num_expected", [
        ("2020-01-01", "2020-01-20", "D", 19),
        ("2020-01-01", "2020-01-25", "D", 24),
        ("2020-01-01", "2020-01-02", "D",  1),
    ])
    def test_backfill_same_quarter(self, from_date_str: str, to_date_str: str, grain_expected: str, num_expected: int):
        to_date: Date = Date(to_date_str)
        from_date: Date = Date(from_date_str)

        had_results = False
        for (grain, num) in to_date.backfill(from_date):
            had_results = True
            assert grain == grain_expected
            assert num == num_expected
        assert had_results

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
            date.fromisoformat(expected_quarter_start),
            date.fromisoformat(expected_quarter_end))