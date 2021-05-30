import pytest

from edgar.utils.repo.http_repo_fs import HttpRepoFS
from edgar.utils.repo.http_tools import get_index_macro
from edgar.utils.repo.repo_fs import RepoFormat, RepoFormatter, RepoObject
from edgar.utils.date.date_utils import DatePeriodType

class TestHttpRepoFS:
    def setUp(self):
        self.__formatter = RepoFormatter(RepoFormat({
            DatePeriodType.DAY: 'master{y}{m:02}{d:02}.idx', DatePeriodType.QUARTER: 'master.idx'},
            ['{index}', '{y}', 'QTR{q}']))
        self.__formatter['index'] = get_index_macro()

    def tearDown(self):
        del self.__formatter

    def test_find_object(self) -> None:
        pass