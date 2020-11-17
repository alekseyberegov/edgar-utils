import pytest
import tempfile
import time

from edgar_utils.repo.repo_fs import RepoEntity
from edgar_utils.date.date_utils import DatePeriodType, Date
from typing import Dict, Iterator, List
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from faker import Faker
from edgar_utils.repo.file_repo_fs import FileObjectLocator, FileRepoDir, FileRepoFS, FileRepoObject
from edgar_utils.tests.globals import YEAR_LIST


class TestFileRepoFS(object):
    def test_list_years(self, fs_root: tempfile.TemporaryDirectory, fake: Faker) -> None:
        fs: FileRepoFS = FileRepoFS(Path(fs_root.name))
        for j in [DatePeriodType.DAY, DatePeriodType.QUARTER]:
            years: List[int] = fs.list_years(j)
            assert max(years) == max(YEAR_LIST)
            for i in YEAR_LIST:
                assert i in years

    @pytest.mark.parametrize("obj_path", [
        ('Q/2020/QTR1/file-0.txt'),
        ('Q/2020/QTR3/file-1.txt'),
    ])
    def test_get_object_success(self, fs_root: tempfile.TemporaryDirectory, obj_path: str):
        root: Path = Path(fs_root.name)
        fs: FileRepoFS = FileRepoFS(root)
        obj: FileRepoObject = fs.get_object(obj_path)
        assert obj is not None
        assert obj.path == root / obj_path

    @pytest.mark.parametrize("obj_path", [
        ('Q/2010/QTR1/file-0.txt'),
        ('Q/2010/QTR3/file-1.txt'),
    ])
    def test_get_object_failure(self, fs_root: tempfile.TemporaryDirectory, obj_path: str):
        root: Path = Path(fs_root.name)
        fs: FileRepoFS = FileRepoFS(root)
        obj: FileRepoObject = fs.get_object(obj_path)
        assert obj is None

    def test_get_update_list(self, edgar_fs: tempfile.TemporaryDirectory):
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root)
        miss: List[str] = fs.get_update_list(Date('2017-09-10'), Date('2019-05-25'), {   
                DatePeriodType.DAY     : 'master{y}{m:02}{d:02}.idx', 
                DatePeriodType.QUARTER : 'master.idx'})
            
        holidays_sample: List[Date] = [
                Date('2018-01-01'), Date('2018-01-15'), Date('2018-02-19'),
                Date('2018-05-13'), Date('2018-05-28'), Date('2018-07-04'),
                Date('2018-09-03'), Date('2018-10-08'), Date('2018-11-12'),
                Date('2018-11-22'), Date('2018-12-25'), Date('2019-01-01'),
                Date('2019-01-21'), Date('2019-02-18'), Date('2019-05-27'),
            ]
        
        qty_count: int = 0
        day_count: int = 0
        for i in miss:
            loc: FileObjectLocator = FileObjectLocator(i)
            if loc[0] == str(DatePeriodType.QUARTER):
                assert loc[-1] == 'master.idx'
                qty_count += 1
            else:
                the_date: Date = loc.date('master{y:04}{m:02}{d:02}.idx')
                assert not the_date.is_weekend()
                assert the_date not in holidays_sample
                day_count += 1

        assert qty_count == 7
        assert day_count == 350

    @pytest.mark.parametrize("path, object_name, expected_result", [
        ('D/2017/QTR3', 'master20170901.idx', ['D', '2017', 'QTR3', 'master20170901.idx']),
        ('D/2018/QTR1', 'master20180102.idx', ['D', '2018', 'QTR1', 'master20180102.idx']),
        ('D/2017/QTR4', 'master20171213.idx', ['D', '2017', 'QTR4', 'master20171213.idx']),
    ])
    def test_new_object(self, edgar_fs: tempfile.TemporaryDirectory, path: str, object_name: str, expected_result: List[str]):
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root)
    
        obj: FileRepoObject = fs.new_object(path, object_name)
        assert obj is not None
        assert obj.subpath(4) == expected_result


