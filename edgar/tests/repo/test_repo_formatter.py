import pytest

from edgar.utils.repo.repo_format import RepoFormatter, RepoFormat
from edgar.utils.date.date_utils import DatePeriodType, Date
from typing import List

class TestRepoFormatter:
    @pytest.mark.parametrize("period_type, date_str, path_spec, name_spec, expected", [
        (DatePeriodType.DAY,    "2020-03-07", ['{t}', '{y}', 'QTR{q}'], 'master{y}{m:02}{d:02}.idx', 'D/2020/QTR1/master20200307.idx'),
        (DatePeriodType.QUARTER,"2020-03-07", ['{t}', '{y}', 'QTR{q}'], 'master.idx', 'Q/2020/QTR1/master.idx'),
    ])
    def test_default(self, period_type: DatePeriodType, date_str: str, 
            path_spec: List[str], name_spec: str, expected: str):
        formatter: RepoFormatter = RepoFormatter(RepoFormat({period_type: name_spec}, path_spec))
        assert '/'.join(formatter.format(period_type, Date(date_str)) ) == expected

    @pytest.mark.parametrize("period_type, date_str, path_spec, name_spec, expected", [
        (DatePeriodType.DAY,    "2020-03-07", ['{z}', '{y}', 'QTR{q}'], 'master{y}{m:02}{d:02}.idx', 'X/2020/QTR1/master20200307.idx'),
        (DatePeriodType.QUARTER,"2020-03-07", ['{z}', '{y}', 'QTR{q}'], 'master.idx', 'X/2020/QTR1/master.idx'),
    ])
    def test_kwargs(self, period_type: DatePeriodType, date_str: str, 
            path_spec: List[str], name_spec: str, expected: str):
        formatter: RepoFormatter = RepoFormatter(RepoFormat({period_type: name_spec}, path_spec))
        assert '/'.join(formatter.format(period_type, Date(date_str), z = 'X') ) == expected

    @pytest.mark.parametrize("period_type, date_str, path_spec, name_spec, expected", [
        (DatePeriodType.DAY,    "2020-03-07", ['{z}', '{y}', 'QTR{q}'], 'master{y}{m:02}{d:02}.idx', 'DAY/2020/QTR1/master20200307.idx'),
        (DatePeriodType.QUARTER,"2020-03-07", ['{z}', '{y}', 'QTR{q}'], 'master.idx', 'QUARTER/2020/QTR1/master.idx'),
    ])
    def test_macros(self, period_type: DatePeriodType, date_str: str, 
            path_spec: List[str], name_spec: str, expected: str):
        formatter: RepoFormatter = RepoFormatter(RepoFormat({period_type: name_spec}, path_spec))
        formatter['z'] = lambda period_type, date: 'DAY' if period_type == DatePeriodType.DAY else 'QUARTER'
        assert '/'.join(formatter.format(period_type, Date(date_str)) ) == expected