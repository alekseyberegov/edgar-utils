import pytest
import tempfile
import unittest

from edgar.utils.repo.repo_fs import RepoFormat, RepoObject
from edgar.utils.date.date_utils import DatePeriodType, Date
from typing import Dict, Iterator, List
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import MagicMock
from faker import Faker
from edgar.utils.repo.file_repo_fs import FileRepoFS
from edgar.utils.repo.file_object_locator import FileObjectLocator
from edgar.utils.repo.file_repo_object import FileRepoObject
from edgar.tests.globals import YEAR_LIST


class TestFileRepoFS:
    REPO_FORMAT: RepoFormat = RepoFormat(
        {DatePeriodType.DAY: 'master{y}{m:02}{d:02}.idx', DatePeriodType.QUARTER : 'master.idx'},
        ['{t}', '{y}', 'QTR{q}']
    )

    @pytest.mark.parametrize("obj_path", [
        ('Q/2020/QTR1/file-0.txt'),
        ('Q/2020/QTR3/file-1.txt'),
    ])
    def test_get_object_success(self, test_fs: tempfile.TemporaryDirectory, obj_path: str):
        root: Path = Path(test_fs.name)
        fs: FileRepoFS = FileRepoFS(root, self.REPO_FORMAT)
        obj: FileRepoObject = fs.get_object(obj_path)
        assert obj is not None
        assert obj.path == (root / obj_path).resolve()

    @pytest.mark.parametrize("obj_path", [
        ('Q/2010/QTR1/file-0.txt'),
        ('Q/2010/QTR3/file-1.txt'),
    ])
    def test_get_object_failure(self, test_fs: tempfile.TemporaryDirectory, obj_path: str):
        root: Path = Path(test_fs.name)
        fs: FileRepoFS = FileRepoFS(root, self.REPO_FORMAT)
        obj: FileRepoObject = fs.get_object(obj_path)
        assert obj is None

    @pytest.mark.parametrize("the_date, date_period, path", [
        (Date('2017-10-01'), DatePeriodType.QUARTER, ['Q','2017', 'QTR4', 'master.idx']),
        (Date('2018-01-01'), DatePeriodType.QUARTER, ['Q','2018', 'QTR1', 'master.idx']),
        (Date('2017-10-01'), DatePeriodType.DAY,     ['D','2017', 'QTR4', 'master20171001.idx']),
        (Date('2017-11-20'), DatePeriodType.DAY,     ['D','2017', 'QTR4', 'master20171120.idx']),
        (Date('2018-01-25'), DatePeriodType.DAY,     ['D','2018', 'QTR1', 'master20180125.idx']),
    ])
    def test_find_object_success(self, edgar_fs: tempfile.TemporaryDirectory, the_date: Date, date_period: DatePeriodType, path: List[str]):
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root, self.REPO_FORMAT)
        obj: FileRepoObject = fs.find(date_period, the_date)
        assert obj.subpath(4) == path

    def test_find_missing(self, edgar_fs: tempfile.TemporaryDirectory):
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root, self.REPO_FORMAT)
        missing: List[str] = fs.find_missing(Date('2017-09-10'), Date('2019-05-25'))
            
        holidays_sample: List[Date] = [
            Date('2018-01-01'), Date('2018-01-15'), Date('2018-02-19'),
            Date('2018-05-13'), Date('2018-05-28'), Date('2018-07-04'),
            Date('2018-09-03'), Date('2018-10-08'), Date('2018-11-12'),
            Date('2018-11-22'), Date('2018-12-25'), Date('2019-01-01'),
            Date('2019-01-21'), Date('2019-02-18'), Date('2019-05-27'),
        ]
        
        q: int = 0
        d: int = 0
        for i in missing:
            loc: FileObjectLocator = FileObjectLocator(i, FileObjectLocator.DEFAULT_PATH_SPEC)
            if loc[0] == str(DatePeriodType.QUARTER):
                assert loc[-1] == 'master.idx'
                q += 1
            else:
                the_date: Date = loc.date('master{y:04}{m:02}{d:02}.idx')
                assert not the_date.is_weekend()
                assert the_date not in holidays_sample
                d += 1

        assert q == 7
        assert d == 350

    @pytest.mark.parametrize("path, object_name, expected_result", [
        ('D/2017/QTR3', 'master20170901.idx', ['D', '2017', 'QTR3', 'master20170901.idx']),
        ('D/2018/QTR1', 'master20180102.idx', ['D', '2018', 'QTR1', 'master20180102.idx']),
        ('D/2017/QTR4', 'master20171213.idx', ['D', '2017', 'QTR4', 'master20171213.idx']),
    ])
    def test_new_object(self, edgar_fs: tempfile.TemporaryDirectory, path: str, object_name: str, expected_result: List[str]):
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root, self.REPO_FORMAT)
        obj: FileRepoObject = fs.new_object(path, object_name)

        assert obj is not None
        assert obj.subpath(4) == expected_result

    @pytest.mark.parametrize("the_date, date_period, path", [
        (Date('1972-12-13'), DatePeriodType.QUARTER, ['Q','1972','QTR4','master.idx']),
        (Date('1974-02-13'), DatePeriodType.QUARTER, ['Q','1974','QTR1','master.idx']),
        (Date('2020-01-05'), DatePeriodType.DAY,     ['D','2020','QTR1','master20200105.idx']),
        (Date('2020-04-25'), DatePeriodType.DAY,     ['D','2020','QTR2','master20200425.idx']),
    ])   
    def test_create(self, edgar_fs: tempfile.TemporaryDirectory, the_date: Date, date_period: DatePeriodType, path: List[str]) -> None:
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root, self.REPO_FORMAT)
        obj: FileRepoObject = fs.create(date_period, the_date)
        assert obj is not None
        assert obj.subpath(4) == path

