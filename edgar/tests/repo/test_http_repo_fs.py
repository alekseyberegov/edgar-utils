import pytest, unittest

from edgar.utils.repo.http_repo_fs import HttpRepoFS
from edgar.utils.repo.http_repo_object import HttpRepoObject
from edgar.utils.repo.http_tools import get_index_macro
from edgar.utils.repo.repo_fs import RepoFormat, RepoFormatter, RepoObject
from edgar.utils.date.date_utils import DatePeriodType, Date

class TestHttpRepoFS:
    def setup_method(self) -> None:
        self.__formatter = RepoFormatter(RepoFormat({
            DatePeriodType.DAY: 'master{y}{m:02}{d:02}.idx', DatePeriodType.QUARTER: 'master.idx'},
            ['{index}', '{y}', 'QTR{q}']))
        self.__formatter['index'] = get_index_macro()

    def teardown_method(self):
        del self.__formatter

    @pytest.mark.parametrize("period_type, date_str, expected", [
        (DatePeriodType.DAY,     '2020-03-17', 'https://www.sec.gov/Archives/edgar/daily-index/2020/QTR1/master20200317.idx'),
        (DatePeriodType.QUARTER, '2021-06-17', 'https://www.sec.gov/Archives/edgar/full-index/2021/QTR2/master.idx')
    ])
    def test_find_object(self, period_type, date_str, expected) -> None:
        repo: HttpRepoFS = HttpRepoFS('https://www.sec.gov/Archives/edgar/', self.__formatter)
        obj: HttpRepoObject = repo.find(period_type, Date(date_str))
        assert obj.as_uri() == expected