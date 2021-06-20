import pytest, tempfile, unittest
from typing import List
from pathlib import Path

from edgar.utils.repo.repo_object_path import RepoObjectPath
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.utils.date.date_utils import Date, DatePeriodType
from edgar.utils.repo.repo_fs import RepoFormat

class TestFileObjectLocator:
    REPO_FORMAT: RepoFormat = RepoFormat(
        {DatePeriodType.DAY: 'master{y:4}{m:02}{d:02}.idx', DatePeriodType.QUARTER : 'master.idx'},
        ['{t}', '{y}', 'QTR{q}']
    )

    @pytest.mark.parametrize("path, date_period, quarter, year, date_str", [
        ('Q/1972/QTR4/master19721213.idx', 'Q', 4, 1972, '1972-12-13'),
        ('Q/2020/QTR1/master20200105.idx', 'Q', 1, 2020, '2020-01-05'),
        ('D/2020/QTR1/master20200125.idx', 'D', 1, 2020, '2020-01-25'),
    ])    
    def test_init_with_path(self, path: str, date_period: str, quarter: int, year: int, date_str: str) -> None:
        obj_path: RepoObjectPath = RepoObjectPath(path, self.REPO_FORMAT)
        assert obj_path.date_period_type() == DatePeriodType.from_string(date_period)
        assert obj_path.year() == year
        assert obj_path.quarter() == quarter
        assert obj_path.date() == Date(date_str)

    @pytest.mark.parametrize("path, date_period, quarter, year, date_str", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q', 4, 1972, '1972-12-13'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q', 1, 2020, '2020-01-05'),
        (['D','2020','QTR1','master20200125.idx'], 'D', 1, 2020, '2020-01-25'),
    ])    
    def test_init_with_list(self, path: List[str], date_period: str, quarter: int, year: int, date_str: str) -> None:
        obj_path: RepoObjectPath = RepoObjectPath(path, self.REPO_FORMAT)
        assert obj_path.date_period_type() == DatePeriodType.from_string(date_period)
        assert obj_path.year() == year
        assert obj_path.quarter() == quarter
        assert obj_path.date() == Date(date_str)

    @pytest.mark.parametrize("path_list, expected_result", [
        (['Q', '2020', 'QTR1', 'file-1.txt'], 'Q/2020/QTR1/file-1.txt'),
        (['Q', '2020', 'QTR3', 'file-2.txt'], 'Q/2020/QTR3/file-2.txt'),
    ])    
    def test_locate_success(self,  test_fs: tempfile.TemporaryDirectory, path_list: List[str], expected_result: str):
        root: Path = Path(test_fs.name)
        dir: FileRepoDir = FileRepoDir(root)
        obj_path: RepoObjectPath = RepoObjectPath.from_object(dir.get(path_list), self.REPO_FORMAT)
        assert str(obj_path) == expected_result
    
    @pytest.mark.parametrize("path, parent", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q/1972/QTR4'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q/2020/QTR1'),
        (['D','2020','QTR1','master20200125.idx'], 'D/2020/QTR1'),
    ])    
    def test_parent_success(self, path:List[str], parent:str):
        obj_path: RepoObjectPath = RepoObjectPath(path, self.REPO_FORMAT)
        assert obj_path.parent() == parent
        
    @pytest.mark.parametrize("path, date_period, quarter, year, date_str", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q', 'QTR4', '1972', '1972-12-13'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q', 'QTR1', '2020', '2020-01-05'),
        (['D','2020','QTR1','master20200125.idx'], 'D', 'QTR1', '2020', '2020-01-25'),
    ])    
    def test_getitem(self, path:List[str], date_period: str, quarter: str, year: int, date_str: str) -> None:
        obj_path: RepoObjectPath = RepoObjectPath(path, self.REPO_FORMAT)
        assert obj_path[0] == date_period
        assert obj_path[1] == year
        assert obj_path[2] == quarter
        assert obj_path[3] == Date(date_str).format('master{y}{m:02}{d:02}.idx')

    @pytest.mark.parametrize("path, expected_result", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q/1972/QTR4/master19721213.idx'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q/2020/QTR1/master20200105.idx'),
        (['D','2020','QTR1','master20200125.idx'], 'D/2020/QTR1/master20200125.idx'),
    ])  
    def test_str(self, path: List[str], expected_result: str) -> None:
        obj_path: RepoObjectPath = RepoObjectPath(path, self.REPO_FORMAT)
        assert str(obj_path) == expected_result
