import pytest

from edgar_utils.date.date_utils import Date

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