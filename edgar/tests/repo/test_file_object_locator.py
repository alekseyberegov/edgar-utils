import pytest, tempfile, unittest
from typing import List
from pathlib import Path

from edgar.utils.repo.file_object_locator import FileObjectLocator
from edgar.utils.repo.file_repo_dir import FileRepoDir
from edgar.utils.date.date_utils import Date, DatePeriodType

class TestFileObjectLocator:
    @pytest.mark.parametrize("path, date_period, quarter, year, date_str", [
        ('Q/1972/QTR4/master19721213.idx', 'Q', 4, 1972, '1972-12-13'),
        ('Q/2020/QTR1/master20200105.idx', 'Q', 1, 2020, '2020-01-05'),
        ('D/2020/QTR1/master20200125.idx', 'D', 1, 2020, '2020-01-25'),
    ])    
    def test_init_with_path(self, path: str, date_period: str, quarter: int, year: int, date_str: str) -> None:
        loc: FileObjectLocator = FileObjectLocator(path, FileObjectLocator.DEFAULT_PATH_SPEC)
        assert loc.date_period() == DatePeriodType.from_string(date_period)
        assert loc.year() == year
        assert loc.quarter() == quarter
        assert loc.date('master{y:04}{m:02}{d:02}.idx') == Date(date_str)

    @pytest.mark.parametrize("path, date_period, quarter, year, date_str", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q', 4, 1972, '1972-12-13'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q', 1, 2020, '2020-01-05'),
        (['D','2020','QTR1','master20200125.idx'], 'D', 1, 2020, '2020-01-25'),
    ])    
    def test_init_with_list(self, path: List[str], date_period: str, quarter: int, year: int, date_str: str) -> None:
        loc: FileObjectLocator = FileObjectLocator(path, FileObjectLocator.DEFAULT_PATH_SPEC)
        assert loc.date_period() == DatePeriodType.from_string(date_period)
        assert loc.year() == year
        assert loc.quarter() == quarter
        assert loc.date('master{y:04}{m:02}{d:02}.idx') == Date(date_str)

    @pytest.mark.parametrize("path_list, expected_result", [
        (['Q', '2020', 'QTR1', 'file-1.txt'], 'Q/2020/QTR1/file-1.txt'),
        (['Q', '2020', 'QTR3', 'file-2.txt'], 'Q/2020/QTR3/file-2.txt'),
    ])    
    def test_locate_success(self,  test_fs: tempfile.TemporaryDirectory, path_list: List[str], expected_result: str):
        root: Path = Path(test_fs.name)
        dir: FileRepoDir = FileRepoDir(root)
        loc: FileObjectLocator = FileObjectLocator.locate(dir.get(path_list), FileObjectLocator.DEFAULT_PATH_SPEC)
        assert str(loc) == expected_result
    
    @pytest.mark.parametrize("path, parent", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q/1972/QTR4'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q/2020/QTR1'),
        (['D','2020','QTR1','master20200125.idx'], 'D/2020/QTR1'),
    ])    
    def test_parent_success(self, path:List[str], parent:str):
        loc: FileObjectLocator = FileObjectLocator(path, FileObjectLocator.DEFAULT_PATH_SPEC)
        assert loc.parent() == parent
        
    @pytest.mark.parametrize("path, date_period, quarter, year, date_str", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q', 'QTR4', '1972', '1972-12-13'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q', 'QTR1', '2020', '2020-01-05'),
        (['D','2020','QTR1','master20200125.idx'], 'D', 'QTR1', '2020', '2020-01-25'),
    ])    
    def test_getitem(self, path:List[str], date_period: str, quarter: str, year: int, date_str: str) -> None:
        loc: FileObjectLocator = FileObjectLocator(path, FileObjectLocator.DEFAULT_PATH_SPEC)
        assert loc[0] == date_period
        assert loc[1] == year
        assert loc[2] == quarter
        assert loc[3] == Date(date_str).format('master{y}{m:02}{d:02}.idx')

    @pytest.mark.parametrize("path, expected_result", [
        (['Q','1972','QTR4','master19721213.idx'], 'Q/1972/QTR4/master19721213.idx'),
        (['Q','2020','QTR1','master20200105.idx'], 'Q/2020/QTR1/master20200105.idx'),
        (['D','2020','QTR1','master20200125.idx'], 'D/2020/QTR1/master20200125.idx'),
    ])  
    def test_str(self, path: List[str], expected_result: str) -> None:
        loc: FileObjectLocator = FileObjectLocator(path, FileObjectLocator.DEFAULT_PATH_SPEC)
        assert str(loc) == expected_result
