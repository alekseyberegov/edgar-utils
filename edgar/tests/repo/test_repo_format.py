import json
import unittest
from edgar.utils.repo.repo_fs import RepoFormat
from edgar.utils.date.date_utils import DatePeriodType
from edgar.utils.repo.serdeser import dataclass_json_dump

class TestRepoFormat(unittest.TestCase):
    def setUp(self) -> None:
        self.repo_format: RepoFormat = RepoFormat(
            {DatePeriodType.DAY: 'master{y}{m:02}{d:02}.idx', DatePeriodType.QUARTER: 'master.idx'},
            ['{t}', '{y}', 'QTR{q}']
        )

    def tearDown(self) -> None:
        del self.repo_format

    def test_json_ser(self) -> None:
        j = json.loads(dataclass_json_dump(self.repo_format))

        assert j['name_spec']['1'] == 'master{y}{m:02}{d:02}.idx'
        assert j['name_spec']['2'] == 'master.idx'
        assert j['path_spec'][ 0 ] == '{t}'
        assert j['path_spec'][ 1 ] == '{y}'
        assert j['path_spec'][ 2 ] == 'QTR{q}'

