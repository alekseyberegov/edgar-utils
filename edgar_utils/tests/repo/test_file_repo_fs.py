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
from edgar_utils.repo.file_repo_fs import FileRepoDir, FileRepoFS, FileRepoObject
from edgar_utils.tests.globals import YEAR_LIST, YEAR_COUNT, YEAR_MAX, FILE_PER_DIR

class TestFileRepoDir(object):
    def test_init_dir_empty(self, dir_empty: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        assert dir.exists()
        assert len(dir) == 0

    def test_init_dir_prepped(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
   
        subdirs: Dict[str,int] = {}
        for (name, _) in dir:
            subdirs[name] = 1
        
        for i in YEAR_LIST:
            assert str(i) in subdirs

    def test_refresh(self, dir_prepped: tempfile.TemporaryDirectory, fake: Faker) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        assert len(dir) == len(YEAR_LIST)

        name: str = fake.file_name()
        path: Path = dir.path / name
        path.mkdir()

        for i in range(2):
            assert len(dir) == len(YEAR_LIST) + i
            assert (lambda x: (x == 0 and name not in dir) or (x == 1 and name in dir))(i)
            dir.refresh()
  
    def test_new_object_success(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name()
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        obj: FileRepoObject = dir.new_object(name)

        assert obj.path.name == name
        assert len(dir) == 1
        for (_, o) in dir:
            assert o == obj

    def test_new_dir_success(self, dir_empty: tempfile.TemporaryDirectory, fake: Faker) -> None:
        name: str = fake.file_name(extension="")
        dir: FileRepoDir = FileRepoDir(Path(dir_empty.name))
        subdir = dir.new_dir(name)

        assert len(dir) == 1
        assert name in dir
        assert subdir.exists()

    def test_lastmodified(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        (timestamp, path) = dir.lastmodified()
        now = datetime.today()

        assert path.name == str(max(y for y in YEAR_LIST))
        assert now > timestamp and timestamp > now - timedelta(seconds = 10)

    def test_sorted_entities(self, dir_prepped: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(dir_prepped.name))
        objects: List = dir.sorted_entities()
        expected: Iterator = iter(sorted(YEAR_LIST, reverse = True))
        for actual in objects:
            assert actual == str(next(expected))

    @pytest.mark.parametrize("path_list, expected_result", [
        (['Q', '2020', 'QTR1', 'file-0.txt'],  'Q/2020/QTR1/file-0.txt' ),
        (['Q', '2020', 'QTR3', 'file-1.txt'],  'Q/2020/QTR3/file-1.txt' ),
    ])
    def test_get_success(self, fs_root: tempfile.TemporaryDirectory, path_list: List[str], expected_result: str):
        root: Path = Path(fs_root.name)
        dir: FileRepoDir = FileRepoDir(root)
        obj: FileRepoObject = dir.get(path_list)
        assert  root / expected_result == obj.path

    @pytest.mark.parametrize("path_list", [
        (['Q', '2200', 'QTR1', 'file-0.txt']),
        (['Q', '2020', 'QTR3', 'file-9.txt']),
    ])
    def test_get_failure(self, fs_root: tempfile.TemporaryDirectory, path_list: List[str]):
        root: Path = Path(fs_root.name)
        dir: FileRepoDir = FileRepoDir(root)
        obj: FileRepoObject = dir.get(path_list)
        assert  obj is None


    def test_visit_all_objects(self, fs_root: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(fs_root.name))
        mock: MagicMock = MagicMock()
        mock.visit.return_value = True
        dir.visit(mock)

        i: int = 0
        for c in mock.mock_calls:
            assert c[0] == 'visit'
            assert isinstance(c[1][0], FileRepoObject)
            assert c[1][0].subpath(4) == [
                "QD"[i // (FILE_PER_DIR * 4 * YEAR_COUNT)],
                "{year}".format(year = YEAR_MAX - (i // (FILE_PER_DIR * 4)) % YEAR_COUNT),
                "QTR{quarter}".format(quarter = 4 - (i // FILE_PER_DIR) % 4),
                "file-{file}.txt".format(file = FILE_PER_DIR - (i % FILE_PER_DIR) - 1)
            ]
            i += 1

        assert len(mock.mock_calls) == FILE_PER_DIR * 4 * YEAR_COUNT * 2

    def test_visit_one_object(self, fs_root: tempfile.TemporaryDirectory) -> None:
        dir: FileRepoDir = FileRepoDir(Path(fs_root.name))
        mock: MagicMock = MagicMock()
        mock.visit.return_value = False
        dir.visit(mock)
        
        c = mock.mock_calls[0]
        assert c[0] == 'visit'
        assert isinstance(c[1][0], FileRepoObject)
        assert c[1][0].subpath(4) == ['Q', str(YEAR_MAX), 'QTR4', 'file-2.txt']
        assert len(mock.mock_calls) == 1

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

    def test_missing(self, edgar_fs: tempfile.TemporaryDirectory):
        root: Path = Path(edgar_fs.name)
        fs: FileRepoFS = FileRepoFS(root)





