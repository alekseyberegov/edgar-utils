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
    def test_quarter(self, date_str, expected_result):
        date_obj = Date(date_str)
        assert date_obj.quarter() == expected_result
